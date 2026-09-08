from __future__ import annotations

from typing import Dict, Tuple
import numpy as np
import pandas as pd


def simulate_two_group(n_control: int, n_treatment: int, control_mean: float, treatment_mean: float, sd: float, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Generate explicitly synthetic two-group observations for design exploration."""
    n_control = max(2, int(n_control)); n_treatment = max(2, int(n_treatment)); sd = max(1e-9, float(sd))
    rng = np.random.default_rng(int(seed))
    control = rng.normal(float(control_mean), sd, n_control)
    treatment = rng.normal(float(treatment_mean), sd, n_treatment)
    df = pd.DataFrame({"Group": ["Control"] * n_control + ["Treatment"] * n_treatment,
                       "Outcome": np.concatenate([control, treatment]),
                       "Synthetic": True})
    diff = float(treatment.mean() - control.mean())
    pooled = np.sqrt(((n_control-1)*control.var(ddof=1) + (n_treatment-1)*treatment.var(ddof=1)) / (n_control+n_treatment-2))
    standardized = diff / pooled if pooled > 0 else np.nan
    summary = {"Control mean": float(control.mean()), "Treatment mean": float(treatment.mean()), "Observed synthetic difference": diff, "Standardized difference": float(standardized) if not np.isnan(standardized) else np.nan}
    return df, summary


def simulation_sensitivity(n_control: int, n_treatment: int, control_mean: float, treatment_mean: float, sd: float, repeats: int = 100, seed: int = 42) -> pd.DataFrame:
    """Repeat synthetic simulations to show sampling variability; never represents real evidence."""
    rows = []
    for i in range(max(1, int(repeats))):
        _, s = simulate_two_group(n_control, n_treatment, control_mean, treatment_mean, sd, seed + i)
        rows.append({"Simulation": i + 1, **s})
    return pd.DataFrame(rows)


def summarize_sensitivity(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {"Simulations": 0}
    x = pd.to_numeric(df["Observed synthetic difference"], errors="coerce").dropna()
    return {"Simulations": int(len(x)), "Mean synthetic difference": float(x.mean()), "SD across simulations": float(x.std(ddof=1)) if len(x) > 1 else 0.0, "5th percentile": float(x.quantile(0.05)), "95th percentile": float(x.quantile(0.95))}


def export_pilot(parameters: Dict[str, object], summary: Dict[str, object], sensitivity: Dict[str, object]) -> str:
    lines = ["# SciMantra Synthetic Pilot Lab", "", "> ALL observations and outcomes in this report are synthetic simulations. They are not experimental evidence.", "", "## Simulation parameters"]
    lines += [f"- **{k}**: {v}" for k, v in parameters.items()]
    lines += ["", "## One synthetic run"] + [f"- **{k}**: {v}" for k, v in summary.items()]
    lines += ["", "## Sensitivity across simulations"] + [f"- **{k}**: {v}" for k, v in sensitivity.items()]
    return "\n".join(lines)
