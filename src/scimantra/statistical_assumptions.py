"""Transparent pre-analysis assumption and analysis-choice planning helpers."""

from __future__ import annotations

from typing import Dict, List

CHECKS = [
    ("Outcome distribution", "Is the outcome compatible with the proposed model family?", "Inspect distribution and consider transformation or an appropriate generalized model."),
    ("Independence / experimental unit", "Are observations genuinely independent at the analysis level?", "Define the experimental unit and account for clustering or repeated observations."),
    ("Variance structure", "Is variance reasonably comparable across groups or correctly modeled?", "Inspect residual spread and use robust, weighted, transformed, or heterogeneous-variance models when justified."),
    ("Repeated measures", "Are multiple measurements from the same unit handled as correlated?", "Use paired/repeated-measures or mixed-effects methods when the design requires them."),
    ("Outliers / influential observations", "Could a small number of observations drive the conclusion?", "Predefine detection, investigation, and sensitivity-analysis rules; never remove points solely to improve significance."),
    ("Missing data", "Could missingness change the analysis or interpretation?", "Describe missingness, preserve denominators, and predefine an appropriate handling/sensitivity strategy."),
    ("Multiplicity", "Are many outcomes, groups, contrasts, or tests being considered?", "Predefine primary contrasts and use an appropriate multiplicity strategy where relevant."),
    ("Model / test choice", "Is the selected analysis tied to the design and estimand rather than convenience?", "Record the scientific question, estimand, design, and rationale before choosing the test/model."),
    ("Transformation / scale", "Would transformation change interpretation or conceal an important feature?", "Justify transformations on measurement/model grounds and report the analysis scale clearly."),
    ("Robustness", "Would plausible alternative assumptions materially change the conclusion?", "Predefine sensitivity or robustness analyses and document deviations."),
]


def default_checks() -> List[Dict[str, object]]:
    return [{"Check": n, "Concern (0-5)": 0, "Readiness (0-5)": 0, "Question": q, "Recommended action": a, "Decision record": ""} for n, q, a in CHECKS]


def audit_check(concern: float, readiness: float) -> float:
    concern = max(0.0, min(5.0, float(concern)))
    readiness = max(0.0, min(5.0, float(readiness)))
    return round(((concern * 0.6) + ((5.0 - readiness) * 0.4)) / 5.0 * 100.0, 1)


def build_audit(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    result = []
    for row in rows:
        score = audit_check(row.get("Concern (0-5)", 0), row.get("Readiness (0-5)", 0))
        result.append({**row, "Analysis-risk index": score, "Priority": "High" if score >= 60 else "Moderate" if score >= 35 else "Lower"})
    return sorted(result, key=lambda x: (-float(x["Analysis-risk index"]), str(x["Check"])))


def audit_summary(audit: List[Dict[str, object]]) -> Dict[str, object]:
    if not audit:
        return {"overall": 0.0, "high": 0, "moderate": 0, "lower": 0, "top": ""}
    vals = [float(x["Analysis-risk index"]) for x in audit]
    return {"overall": round(sum(vals) / len(vals), 1), "high": sum(x["Priority"] == "High" for x in audit), "moderate": sum(x["Priority"] == "Moderate" for x in audit), "lower": sum(x["Priority"] == "Lower" for x in audit), "top": str(audit[0]["Check"])}


def analysis_options(design: str) -> List[str]:
    d = design.lower()
    if "paired" in d or "repeat" in d or "longitud" in d:
        return ["Paired / repeated-measures analysis", "Mixed-effects model", "Generalized estimating approach", "Other — justify"]
    if "count" in d:
        return ["Poisson / negative-binomial model", "Nonparametric approach", "Other — justify"]
    if "binary" in d or "case" in d:
        return ["Logistic regression", "Contingency-table analysis", "Other — justify"]
    return ["Linear model / ANOVA", "Generalized linear model", "Rank-based / nonparametric analysis", "Permutation / resampling analysis", "Other — justify"]


def export_audit(audit: List[Dict[str, object]], summary: Dict[str, object], analysis_choice: str) -> str:
    lines = ["# Statistical Assumption & Analysis-Choice Record", "", f"Proposed analysis: {analysis_choice or 'Not selected'}", f"Overall analysis-risk index: {summary.get('overall', 0)}", "", "> Planning aid only. It does not certify assumptions or select an analysis automatically.", ""]
    for row in audit:
        lines += [f"## {row['Check']}", f"- Concern: {row['Concern (0-5)']}/5", f"- Readiness: {row['Readiness (0-5)']}/5", f"- Risk index: {row['Analysis-risk index']}", f"- Priority: {row['Priority']}", f"- Action: {row['Recommended action']}", f"- Decision record: {row.get('Decision record', '')}", ""]
    return "\n".join(lines)
