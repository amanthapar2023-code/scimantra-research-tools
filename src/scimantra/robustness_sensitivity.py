"""Research robustness and sensitivity planning engine.

This module maps researcher-defined perturbations to conclusion stability. It
is a planning/audit framework and does not claim to simulate or estimate
unobserved scientific effects without data.
"""

from __future__ import annotations

from typing import Dict, List

SCENARIOS = [
    ("Outlier / influence change", "Remove or down-weight influential observations using a prespecified rule.", "Does the direction of the main conclusion change?"),
    ("Missing-data assumption", "Compare the planned missing-data strategy with a defensible alternative.", "Does the conclusion depend on the missingness handling?"),
    ("Model specification", "Compare the primary model with a scientifically justified alternative.", "Is the conclusion robust to reasonable model choice?"),
    ("Covariate adjustment", "Compare the prespecified adjustment set with a defensible sensitivity set.", "Does adjustment materially alter the conclusion?"),
    ("Transformation / scale", "Test a justified alternative scale or transformation when appropriate.", "Does the inference depend on the measurement scale?"),
    ("Exclusion rule", "Apply a prespecified alternative for a potentially influential exclusion criterion.", "Does an exclusion decision drive the result?"),
    ("Time / batch subset", "Check important temporal, batch, site, or operator strata separately.", "Does the conclusion persist across meaningful strata?"),
    ("Multiplicity / outcome focus", "Compare the primary conclusion with the broader prespecified outcome family.", "Does the conclusion survive multiplicity-aware interpretation?"),
    ("Negative-control challenge", "Use an appropriate negative control when scientifically available.", "Does the control reveal systematic residual structure?"),
]


def scenario_rows() -> List[Dict[str, object]]:
    return [{
        "Scenario": n,
        "Perturbation": p,
        "Question": q,
        "Direction preserved": "Unknown",
        "Effect magnitude change (%)": 0.0,
        "Confidence change": "Unknown",
        "Evidence / notes": "",
    } for n, p, q in SCENARIOS]


def classify_stability(direction: str, magnitude_change: float, confidence_change: str) -> str:
    if direction == "Reversed":
        return "Fragile"
    if direction == "Unchanged" and abs(float(magnitude_change)) <= 10 and confidence_change in {"Unchanged", "Higher"}:
        return "Stable"
    if direction == "Unchanged" and abs(float(magnitude_change)) <= 25:
        return "Mostly stable"
    if direction in {"Unknown", "Not run"}:
        return "Not assessed"
    return "Sensitive"


def build_robustness_map(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out = []
    for row in rows:
        item = dict(row)
        item["Stability"] = classify_stability(
            str(row.get("Direction preserved", "Unknown")),
            float(row.get("Effect magnitude change (%)", 0) or 0),
            str(row.get("Confidence change", "Unknown")),
        )
        out.append(item)
    return out


def stability_summary(rows: List[Dict[str, object]]) -> Dict[str, object]:
    counts = {"Stable": 0, "Mostly stable": 0, "Sensitive": 0, "Fragile": 0, "Not assessed": 0}
    for r in rows:
        counts[str(r.get("Stability", "Not assessed"))] = counts.get(str(r.get("Stability", "Not assessed")), 0) + 1
    assessed = len(rows) - counts["Not assessed"]
    robust = counts["Stable"] + counts["Mostly stable"]
    score = round(100 * robust / assessed, 1) if assessed else 0.0
    return {**counts, "assessed": assessed, "robustness_score": score}


def fragile_scenarios(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return [r for r in rows if r.get("Stability") in {"Fragile", "Sensitive"}]


def export_robustness(rows: List[Dict[str, object]], summary: Dict[str, object]) -> str:
    lines = ["# Research Robustness & Sensitivity Map", "", "> Researcher-entered sensitivity audit. It does not estimate true causal robustness without appropriate data.", "", f"Robustness score among assessed scenarios: {summary['robustness_score']}", ""]
    for r in rows:
        lines.extend([
            f"## {r['Scenario']}",
            f"- Perturbation: {r['Perturbation']}",
            f"- Direction preserved: {r['Direction preserved']}",
            f"- Effect magnitude change: {r['Effect magnitude change (%)']}%",
            f"- Confidence change: {r['Confidence change']}",
            f"- Stability: {r['Stability']}",
            f"- Notes: {r.get('Evidence / notes', '')}",
            "",
        ])
    return "\n".join(lines)
