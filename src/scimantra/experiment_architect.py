from typing import Dict, List


def architect(question: str, hypothesis: str, factor: str, outcome: str, comparator: str, secondary_factor: str = "", system: str = "", conditions: str = "", falsifier: str = "") -> Dict[str, object]:
    return {
        "Research question": question.strip(),
        "Hypothesis": hypothesis.strip(),
        "Primary factor / exposure": factor.strip(),
        "Primary outcome": outcome.strip(),
        "Comparator": comparator.strip(),
        "Secondary factor / moderator": secondary_factor.strip(),
        "Population / experimental system": system.strip(),
        "Key experimental conditions": conditions.strip(),
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
    rows = []
    placeholder_prefixes = ("Define", "Specify", "List", "Pre-specify", "Record", "State")
    for label, key in checks:
        value = str(plan.get(key, "")).strip()
        rows.append({"Check": label, "Status": "Addressed" if value and not value.startswith(placeholder_prefixes) else "Needs researcher detail", "Field": key})
    return rows


def architecture_score(rows: List[Dict[str, str]]) -> float:
    return round(100 * sum(r["Status"] == "Addressed" for r in rows) / len(rows), 1) if rows else 0.0


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
    for key, value in plan.items():
        lines += [f"## {key}", str(value), ""]
    lines += ["## Audit", "", "| Check | Status |", "|---|---|"]
    lines += [f"| {r['Check']} | {r['Status']} |" for r in audit]
    lines.append("")
    lines.append("> This is an editable study-design blueprint, not a guarantee that the design is valid for a particular scientific field.")
    return "\n".join(lines)
