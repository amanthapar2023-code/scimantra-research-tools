"""Bias and error-budget planning helpers for research design.

Scores are transparent planning heuristics. They are not estimates of actual
bias, effect size, validity, or publication probability.
"""

from __future__ import annotations

from typing import Dict, List


DOMAINS = [
    ("Selection bias", "Could who enters, remains in, or is excluded from the study differ systematically?", "Predefine eligibility, recruitment, exclusion, and attrition rules."),
    ("Measurement bias", "Could exposure, outcome, or measurement quality differ systematically across conditions?", "Standardize measurement, blind assessment where appropriate, and define QC criteria."),
    ("Confounding", "Could a third variable explain part of the observed relationship?", "Identify plausible pre-exposure confounders and prespecify design or analysis handling."),
    ("Attrition / missingness", "Could missing observations depend on group, exposure, outcome, or protocol deviations?", "Track missingness and predefine missing-data and sensitivity procedures."),
    ("Batch / temporal effects", "Could operator, instrument, batch, day, site, or season track with the factor?", "Randomize or block across batches and preserve provenance."),
    ("Analytical flexibility", "Could multiple reasonable analysis choices change the conclusion?", "Predefine primary outcomes, models, contrasts, exclusions, and sensitivity analyses."),
    ("Reporting bias", "Could only favorable outcomes, analyses, or figures be selected for reporting?", "Maintain an outcome/analysis inventory and document deviations and null findings."),
    ("Pseudoreplication", "Could technical repeats be mistaken for independent experimental units?", "Define the true experimental unit and analyze at the appropriate level."),
]


def domain_rows() -> List[Dict[str, object]]:
    return [
        {
            "Domain": name,
            "Risk (0-5)": 0,
            "Detectability (0-5)": 3,
            "Control strength (0-5)": 0,
            "Question": question,
            "Mitigation": mitigation,
            "Researcher evidence / notes": "",
        }
        for name, question, mitigation in DOMAINS
    ]


def score_domain(risk: float, detectability: float, control: float) -> float:
    """Return a 0-100 residual-risk heuristic; higher means more concern."""
    risk = max(0.0, min(5.0, float(risk)))
    detectability = max(0.0, min(5.0, float(detectability)))
    control = max(0.0, min(5.0, float(control)))
    residual = risk * 0.5 + (5.0 - control) * 0.3 + detectability * 0.2
    return round(residual / 5.0 * 100.0, 1)


def build_budget(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    budget = []
    for row in rows:
        residual = score_domain(row.get("Risk (0-5)", 0), row.get("Detectability (0-5)", 3), row.get("Control strength (0-5)", 0))
        priority = "High" if residual >= 60 else "Moderate" if residual >= 35 else "Lower"
        budget.append({**row, "Residual risk index": residual, "Priority": priority})
    return sorted(budget, key=lambda x: (-float(x["Residual risk index"]), str(x["Domain"])))


def budget_summary(budget: List[Dict[str, object]]) -> Dict[str, object]:
    if not budget:
        return {"overall": 0.0, "high": 0, "moderate": 0, "lower": 0, "top_domain": ""}
    values = [float(x["Residual risk index"]) for x in budget]
    return {
        "overall": round(sum(values) / len(values), 1),
        "high": sum(x["Priority"] == "High" for x in budget),
        "moderate": sum(x["Priority"] == "Moderate" for x in budget),
        "lower": sum(x["Priority"] == "Lower" for x in budget),
        "top_domain": str(budget[0]["Domain"]),
    }


def mitigation_actions(budget: List[Dict[str, object]]) -> List[Dict[str, object]]:
    actions = []
    for row in budget:
        if float(row["Residual risk index"]) >= 35:
            actions.append({
                "Priority": row["Priority"],
                "Bias / error domain": row["Domain"],
                "Action": row["Mitigation"],
                "Why": "Reduce or document a major source of uncertainty before final interpretation.",
            })
    return actions


def export_budget(budget: List[Dict[str, object]], summary: Dict[str, object]) -> str:
    lines = ["# Bias & Error Budget Lab", "", "> Planning heuristic only. Scores are not estimates of actual bias or validity.", "", f"Overall residual-risk index: {summary.get('overall', 0)}", ""]
    for row in budget:
        lines.extend([
            f"## {row['Domain']}",
            f"- Risk: {row['Risk (0-5)']}/5",
            f"- Detectability: {row['Detectability (0-5)']}/5",
            f"- Control strength: {row['Control strength (0-5)']}/5",
            f"- Residual-risk index: {row['Residual risk index']}",
            f"- Priority: {row['Priority']}",
            f"- Mitigation: {row['Mitigation']}",
            f"- Researcher notes: {row.get('Researcher evidence / notes', '')}",
            "",
        ])
    return "\n".join(lines)
