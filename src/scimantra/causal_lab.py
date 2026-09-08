"""Causal inference planning and confounding audit helpers.

The engine structures causal-design questions. It does not infer causality
from observational data and does not estimate treatment effects.
"""

from __future__ import annotations

from typing import Dict, List


CHECKS = [
    ("Temporal ordering", "Can the proposed cause occur before the outcome?", "Define exposure/intervention timing and outcome measurement timing."),
    ("Comparator", "Is there a credible reference condition?", "Specify the comparator and why it represents the relevant counterfactual."),
    ("Confounders", "Which variables could influence both factor and outcome?", "Measure plausible pre-exposure confounders and prespecify handling."),
    ("Selection", "Could inclusion, exclusion, or attrition create the association?", "Document selection rules, attrition, and missing-data handling."),
    ("Measurement", "Could exposure or outcome measurement differ by group?", "Use blinded or standardized measurement and predefined QC where appropriate."),
    ("Post-exposure variables", "Are any proposed adjustment variables consequences of the exposure?", "Separate pre-exposure confounders from mediators/colliders before adjustment."),
    ("Randomization / allocation", "Can allocation be randomized or otherwise strengthened?", "Use randomized or blocked allocation when scientifically and practically justified."),
    ("Negative control", "Would a negative-control exposure or outcome help challenge the causal story?", "Specify a scientifically defensible negative control if applicable."),
    ("Sensitivity", "How dependent is the conclusion on plausible unmeasured bias?", "Predefine sensitivity or robustness analyses appropriate to the design."),
    ("Causal claim scope", "Does the proposed conclusion match the study design?", "Limit wording to the causal strength justified by the design and assumptions."),
]


def causal_design_audit(
    hypothesis: str,
    factor: str = "",
    outcome: str = "",
    comparator: str = "",
    design: str = "",
) -> List[Dict[str, str]]:
    """Return an editable causal-design checklist."""
    supplied = {
        "Temporal ordering": bool(factor.strip() and outcome.strip()),
        "Comparator": bool(comparator.strip()),
        "Confounders": False,
        "Selection": False,
        "Measurement": False,
        "Post-exposure variables": False,
        "Randomization / allocation": "random" in design.lower() or "random" in hypothesis.lower(),
        "Negative control": False,
        "Sensitivity": False,
        "Causal claim scope": bool(hypothesis.strip()),
    }
    return [
        {
            "Check": name,
            "Question": question,
            "Recommended evidence / design action": action,
            "Status": "Addressed" if supplied.get(name, False) else "Needs review",
            "Researcher notes": "",
        }
        for name, question, action in CHECKS
    ]


def confounder_candidates(text: str) -> List[str]:
    """Surface generic confounding domains for researcher review, not actual confounders."""
    base = [
        "Baseline characteristics",
        "Batch / operator / instrument",
        "Time / season / measurement occasion",
        "Dose / intensity / duration",
        "Environmental conditions",
        "Selection / eligibility",
        "Concurrent exposures or interventions",
        "Technical measurement quality",
    ]
    return base if text.strip() else []


def audit_score(rows: List[Dict[str, str]]) -> float:
    if not rows:
        return 0.0
    addressed = sum(row.get("Status") == "Addressed" for row in rows)
    return round(100 * addressed / len(rows), 1)


def causal_claim_levels() -> List[Dict[str, str]]:
    return [
        {"Level": "Descriptive", "Permitted use": "Report what was measured or observed.", "Extra burden": "Clear measurement provenance."},
        {"Level": "Associational", "Permitted use": "Describe an observed relationship.", "Extra burden": "Appropriate comparator and uncertainty."},
        {"Level": "Causal", "Permitted use": "Argue that changing the factor changes the outcome.", "Extra burden": "Design, temporal ordering, confounding control, and assumptions must support the claim."},
        {"Level": "Mechanistic", "Permitted use": "Propose how the effect occurs.", "Extra burden": "Direct mechanistic evidence or clearly labeled hypothesis; alternatives must be addressed."},
    ]


def export_causal_audit(rows: List[Dict[str, str]], candidates: List[str]) -> str:
    lines = ["# Causal Inference & Confounding Lab", "", "> Planning audit only. It does not establish causality.", ""]
    lines.append("## Confounder domains for review")
    lines.extend(f"- {x}" for x in candidates)
    lines.append("")
    lines.append("## Causal-design audit")
    for row in rows:
        lines.extend([
            f"### {row['Check']}",
            f"- Question: {row['Question']}",
            f"- Action: {row['Recommended evidence / design action']}",
            f"- Status: {row['Status']}",
            f"- Notes: {row['Researcher notes']}",
            "",
        ])
    return "\n".join(lines)
