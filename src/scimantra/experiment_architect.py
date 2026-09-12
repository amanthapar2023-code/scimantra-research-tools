from typing import Dict, List


def architect(question: str, hypothesis: str, factor: str, outcome: str, comparator: str, secondary_factor: str = "", system: str = "", conditions: str = "", falsifier: str = "") -> Dict[str, object]:
    return {
        "Research question": question.strip(), "Hypothesis": hypothesis.strip(),
        "Primary factor / exposure": factor.strip(), "Primary outcome": outcome.strip(),
        "Comparator": comparator.strip(), "Secondary factor / moderator": secondary_factor.strip(),
        "Population / experimental system": system.strip(), "Key experimental conditions": conditions.strip(),
        "Experimental unit": "Define the smallest independent unit receiving the condition or contributing an independent observation.",
        "Secondary outcomes": "Specify before data collection; distinguish exploratory from confirmatory outcomes.",
        "Controls": "Define negative, positive, vehicle, sham, baseline, or other appropriate controls as applicable.",
        "Replication": "Specify independent biological/experimental replicates separately from technical repeats.",
        "Randomization": "Define how experimental units will be assigned to conditions, if applicable.",
        "Blinding": "Define who is blinded, to what, and how allocation is concealed, if applicable.",
        "Confounders": "List measured and plausible confounders and how they will be controlled or modeled.",
        "Measurement plan": "Define instrument/method, units, timing, QC criteria, detection limits, and missing-data handling.",
        "Analysis plan": "Pre-specify primary comparison/model, effect measure, uncertainty interval, assumptions, and multiplicity handling.",
        "Falsification criterion": falsifier.strip() or "State what observation would count against the primary hypothesis.",
        "Reproducibility": "Record protocol version, sample/data provenance, analysis code, software versions, and deviations.",
    }

DESIGN_FIELDS = [
    ("Experimental unit", "experimental_structure", "What is the smallest independent unit that receives the condition or contributes an independent observation?"),
    ("Secondary outcomes", "outcomes", "List secondary/exploratory outcomes and label which are confirmatory versus exploratory."),
    ("Controls", "controls", "List the controls actually planned and explain what alternative explanation each control addresses."),
    ("Independent replication", "replication", "State the planned number/type of independent experimental units per condition, if known, and distinguish technical repeats."),
    ("Randomization", "randomization", "Describe assignment of independent units to conditions, or state why randomization is not applicable."),
    ("Blinding", "blinding", "State who is blinded, what is concealed, and when; or state why blinding is not applicable."),
    ("Confounders", "confounders", "List plausible confounders and how each will be controlled, balanced, measured, or modeled."),
    ("Measurement QC", "measurement", "Specify measurement method/instrument, units, timing, calibration/QC, detection limits, and missing-data handling."),
    ("Analysis plan", "analysis", "Pre-specify the primary comparison/model, effect measure, uncertainty interval, assumptions, and what happens if assumptions fail."),
    ("Reproducibility", "reproducibility", "Record protocol version, sample/data provenance, analysis code, software versions, and deviations."),
]
PLACEHOLDER_PREFIXES = ("Define", "Specify", "List", "Pre-specify", "Record", "State")


def _addressed(value: object) -> bool:
    text = str(value or "").strip()
    return bool(text) and not text.startswith(PLACEHOLDER_PREFIXES)


def audit_architecture(plan: Dict[str, str]) -> List[Dict[str, str]]:
    checks = [
        ("Primary question", "Research question"), ("Primary hypothesis", "Hypothesis"),
        ("Primary factor", "Primary factor / exposure"), ("Primary outcome", "Primary outcome"),
        ("Comparator", "Comparator"), ("Secondary factor", "Secondary factor / moderator"),
        ("Population / system", "Population / experimental system"), ("Experimental conditions", "Key experimental conditions"),
        ("Experimental unit", "Experimental unit"), ("Controls", "Controls"),
        ("Independent replication", "Replication"), ("Randomization", "Randomization"),
        ("Blinding", "Blinding"), ("Confounders", "Confounders"),
        ("Measurement QC", "Measurement plan"), ("Analysis plan", "Analysis plan"),
        ("Falsification", "Falsification criterion"), ("Reproducibility", "Reproducibility"),
    ]
    return [{"Check": label, "Status": "Addressed" if _addressed(plan.get(key, "")) else "Needs researcher detail", "Field": key} for label, key in checks]


def architecture_score(rows: List[Dict[str, str]]) -> float:
    return round(100 * sum(r["Status"] == "Addressed" for r in rows) / len(rows), 1) if rows else 0.0


def design_specification(plan: Dict[str, str], responses: Dict[str, str]) -> Dict[str, str]:
    """Merge researcher decisions into the architecture; never invent missing design details."""
    merged = dict(plan)
    mapping = {
        "experimental_structure": "Experimental unit", "outcomes": "Secondary outcomes", "controls": "Controls",
        "replication": "Replication", "randomization": "Randomization", "blinding": "Blinding",
        "confounders": "Confounders", "measurement": "Measurement plan", "analysis": "Analysis plan",
        "reproducibility": "Reproducibility",
    }
    for source_key, target_key in mapping.items():
        value = str(responses.get(source_key, "")).strip()
        if value:
            merged[target_key] = value
    return merged


def design_completion(rows: List[Dict[str, str]]) -> Dict[str, object]:
    groups = {
        "Research foundation": ["Primary question", "Primary hypothesis", "Primary factor", "Primary outcome", "Comparator", "Secondary factor", "Population / system", "Experimental conditions", "Falsification"],
        "Experimental structure": ["Experimental unit", "Controls", "Independent replication", "Randomization", "Blinding", "Confounders"],
        "Measurement plan": ["Measurement QC"], "Statistical design": ["Analysis plan"], "Reproducibility": ["Reproducibility"],
    }
    by_check = {r["Check"]: r["Status"] == "Addressed" for r in rows}
    result: Dict[str, object] = {"overall": architecture_score(rows), "groups": {}}
    for name, checks in groups.items():
        done = sum(bool(by_check.get(c, False)) for c in checks)
        result["groups"][name] = {"complete": done, "total": len(checks), "percent": round(100 * done / len(checks), 1)}
    required = ["Experimental unit", "Controls", "Independent replication", "Confounders", "Measurement QC", "Analysis plan", "Reproducibility"]
    result["analysis_ready"] = all(by_check.get(c, False) for c in required)
    result["blocking_checks"] = [c for c in required if not by_check.get(c, False)]
    return result


def reviewer_challenges(plan: Dict[str, str]) -> List[str]:
    return [
        "Is the experimental unit truly independent, or could pseudoreplication inflate N?",
        "Is the comparator capable of answering the stated research question?",
        "Could an unmeasured confounder explain the observed difference?",
        "Are controls sufficient to distinguish the proposed mechanism from alternatives?",
        "Was replication defined before data collection, and is it independent?",
        "Could measurement error, batch effects, or detection limits alter the conclusion?",
        "What analysis decision would change if assumptions fail?",
        "What result would falsify the primary hypothesis?",
        "Are secondary/exploratory outcomes clearly separated from the primary endpoint?",
        "Can another researcher reproduce the protocol and analysis from the recorded materials?",
    ]


def export_architecture(plan: Dict[str, object], audit: List[Dict[str, str]]) -> str:
    lines = ["# SciMantra Research Experiment Architecture", ""]
    for key, value in plan.items(): lines += [f"## {key}", str(value), ""]
    lines += ["## Audit", "", "| Check | Status |", "|---|---|"]
    lines += [f"| {r['Check']} | {r['Status']} |" for r in audit]
    lines += ["", "> This is an editable study-design blueprint, not a guarantee that the design is valid for a particular scientific field."]
    return "\n".join(lines)
