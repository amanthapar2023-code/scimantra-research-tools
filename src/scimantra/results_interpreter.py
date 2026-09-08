"""Transparent results interpreter for researcher-supplied data.

This module computes descriptive statistics and effect summaries from numeric
CSV-like data. It never fabricates observations or converts statistical output
into a causal scientific claim without researcher interpretation.
"""
from __future__ import annotations

from typing import Any
import math
import pandas as pd


def summarize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.select_dtypes(include="number").columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) == 0:
            continue
        rows.append({
            "Variable": col,
            "N": int(s.size),
            "Mean": float(s.mean()),
            "SD": float(s.std(ddof=1)) if len(s) > 1 else math.nan,
            "Median": float(s.median()),
            "Min": float(s.min()),
            "Max": float(s.max()),
        })
    return pd.DataFrame(rows)


def compare_groups(df: pd.DataFrame, outcome: str, group: str) -> dict[str, Any]:
    if outcome not in df.columns or group not in df.columns:
        return {"status": "MISSING_COLUMNS"}
    work = df[[outcome, group]].copy()
    work[outcome] = pd.to_numeric(work[outcome], errors="coerce")
    work = work.dropna()
    groups = list(work[group].astype(str).unique())
    if len(groups) != 2:
        return {"status": "REQUIRES_EXACTLY_TWO_GROUPS", "groups": groups}
    a = work.loc[work[group].astype(str) == groups[0], outcome]
    b = work.loc[work[group].astype(str) == groups[1], outcome]
    mean_a, mean_b = float(a.mean()), float(b.mean())
    pooled_sd = math.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1)) / max(1, len(a)+len(b)-2)) if len(a)>1 and len(b)>1 else math.nan
    effect = (mean_a - mean_b) / pooled_sd if pooled_sd and not math.isnan(pooled_sd) else math.nan
    return {"status": "OK", "group_a": groups[0], "group_b": groups[1], "n_a": len(a), "n_b": len(b), "mean_a": mean_a, "mean_b": mean_b, "difference": mean_a-mean_b, "standardized_difference": effect}


def interpretation_flags(summary: pd.DataFrame, comparison: dict[str, Any]) -> list[str]:
    flags = []
    if summary.empty:
        flags.append("No numeric outcome columns were detected.")
    else:
        flags.append("Descriptive statistics summarize the supplied data; they do not establish causality.")
    if comparison.get("status") == "OK":
        flags.append("The group difference is an effect-size description, not proof that the group caused the difference.")
        if comparison.get("n_a", 0) < 3 or comparison.get("n_b", 0) < 3:
            flags.append("Very small group counts: interpret estimates cautiously and inspect the experimental-unit definition.")
    return flags
