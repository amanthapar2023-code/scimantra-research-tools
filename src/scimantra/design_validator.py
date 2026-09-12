import re
from typing import Dict, List


def _clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _present(value: object) -> bool:
    return bool(_clean(value))


def validate_design(plan: Dict[str, object]) -> List[Dict[str, str]]:
    """Run a conservative design-quality validation without inventing scientific details."""
    question = _clean(plan.get("Research question"))
    hypothesis = _clean(plan.get("Hypothesis"))
    factor = _clean(plan.get("Primary factor / exposure"))
    outcome = _clean(plan.get("Primary outcome"))
    comparator = _clean(plan.get("Comparator"))
    secondary = _clean(plan.get("Secondary factor / moderator"))
    system = _clean(plan.get("Population / experimental system"))
    conditions = _clean(plan.get("Key experimental conditions"))
    unit = _clean(plan.get("Experimental unit"))
    controls = _clean(plan.get("Controls"))
    replication = _clean(plan.get("Replication"))
    randomization = _clean(plan.get("Randomization"))
    blinding = _clean(plan.get("Blinding"))
    confounders = _clean(plan.get("Confounders"))
    measurement = _clean(plan.get("Measurement plan"))
    analysis = _clean(plan.get("Analysis plan"))
    falsifier = _clean(plan.get("Falsification criterion"))
    reproducibility = _clean(plan.get("Reproducibility"))

    rows: List[Dict[str, str]] = []

    def add(check: str, status: str, severity: str, finding: str, action: str) -> None:
        rows.append({"Check": check, "Status": status, "Severity": severity, "Finding": finding, "Action": action})

    add("Research question defined", "Pass" if question else "Block", "Critical", "Question recorded." if question else "No research question is recorded.", "Record the exact question the study will test." if not question else "")
    add("Primary hypothesis defined", "Pass" if hypothesis else "Block", "Critical", "Hypothesis recorded." if hypothesis else "No primary hypothesis is recorded.", "Record a testable hypothesis or explicitly document that the study is exploratory." if not hypothesis else "")
    add("Primary factor operationalized", "Pass" if factor else "Block", "Critical", "Primary factor/exposure is named." if factor else "The primary factor is missing.", "Define what is manipulated, assigned, measured, or compared." if not factor else "")
    add("Primary outcome operationalized", "Pass" if outcome else "Block", "Critical", "Primary outcome is named." if outcome else "The primary outcome is missing.", "Define the measurable endpoint, units, timing, and calculation." if not outcome else "")
    add("Experimental system defined", "Pass" if system else "Block", "Critical", "System/population is recorded." if system else "The experimental system is missing.", "Define the biological system, material, population, or experimental unit context." if not system else "")
    add("Key conditions recorded", "Pass" if conditions else "Warn", "High", "Key conditions are recorded." if conditions else "Important study conditions are not recorded.", "Record environmental, temporal, dose, and protocol conditions that could affect interpretation." if not conditions else "")
    add("Experimental unit defined", "Pass" if unit and not unit.lower().startswith(("define ", "specify ")) else "Block", "Critical", "Experimental unit is explicitly defined." if unit and not unit.lower().startswith(("define ", "specify ")) else "The smallest independent unit is not operationally defined.", "State exactly what receives the condition and what counts as one independent observation." if not (unit and not unit.lower().startswith(("define ", "specify "))) else "")
    add("Independent replication defined", "Pass" if replication and not replication.lower().startswith(("specify ", "define ")) else "Block", "Critical", "Replication information is recorded." if replication and not replication.lower().startswith(("specify ", "define ")) else "Independent replication is not defined.", "State independent biological/experimental replicates and distinguish them from technical repeats." if not (replication and not replication.lower().startswith(("specify ", "define "))) else "")
    add("Controls address alternatives", "Pass" if controls and not controls.lower().startswith(("define ", "list ")) else "Warn", "High", "Controls are recorded." if controls and not controls.lower().startswith(("define ", "list ")) else "Controls are missing or remain generic.", "List the actual controls and state which alternative explanation each addresses." if not (controls and not controls.lower().startswith(("define ", "list "))) else "")
    add("Comparator is specified", "Pass" if comparator else "Warn", "High", "Comparator/reference condition is recorded." if comparator else "No comparator is recorded.", "Define the reference condition when the question requires a comparison." if not comparator else "")
    add("Confounders considered", "Pass" if confounders and not confounders.lower().startswith(("list ", "define ")) else "Warn", "High", "Confounders and handling are recorded." if confounders and not confounders.lower().startswith(("list ", "define ")) else "Potential confounders are not concretely addressed.", "List plausible confounders and how they will be controlled, balanced, measured, or modeled." if not (confounders and not confounders.lower().startswith(("list ", "define "))) else "")
    add("Measurement and QC defined", "Pass" if measurement and not measurement.lower().startswith(("specify ", "define ")) else "Block", "Critical", "Measurement/QC plan is recorded." if measurement and not measurement.lower().startswith(("specify ", "define ")) else "Measurement method or QC remains unspecified.", "Record method/instrument, units, timing, calibration/QC, detection limits, and missing-data handling." if not (measurement and not measurement.lower().startswith(("specify ", "define "))) else "")
    add("Analysis decision pre-specified", "Pass" if analysis and not analysis.lower().startswith(("pre-specify ", "specify ")) else "Block", "Critical", "Analysis plan is recorded." if analysis and not analysis.lower().startswith(("pre-specify ", "specify ")) else "Primary analysis remains unspecified.", "Record the primary comparison/model, effect measure, uncertainty, assumptions, and fallback decisions." if not (analysis and not analysis.lower().startswith(("pre-specify ", "specify "))) else "")
    add("Falsifier is operational", "Pass" if falsifier and not falsifier.lower().startswith(("state ", "what observation")) else "Warn", "High", "A falsification criterion is recorded." if falsifier and not falsifier.lower().startswith(("state ", "what observation")) else "The falsifier is generic or missing.", "Define the observable result and pre-specified decision rule that would count against the hypothesis." if not (falsifier and not falsifier.lower().startswith(("state ", "what observation"))) else "")
    add("Reproducibility record defined", "Pass" if reproducibility and not reproducibility.lower().startswith(("record ", "define ")) else "Warn", "Medium", "Reproducibility materials are recorded." if reproducibility and not reproducibility.lower().startswith(("record ", "define ")) else "Reproducibility documentation remains generic.", "Record protocol version, provenance, analysis code, software versions, and deviations." if not (reproducibility and not reproducibility.lower().startswith(("record ", "define "))) else "")

    # Cross-field consistency checks.
    treatment_words = r"\b(treatment|control|abiotic|biotic|microbial|untreated|vehicle|placebo)\b"
    dose_words = r"\b(concentration|dose|level|exposure|intensity|amount|ppm|mg/?l|mg/kg)\b"
    if factor and comparator and re.search(treatment_words, comparator, re.I) and re.search(dose_words, factor, re.I):
        add("Factor/comparator conceptual alignment", "Review", "High", "The factor reads like a dose/exposure while the comparator reads like a treatment/control condition.", "Confirm whether treatment and dose are separate design factors rather than forcing them into one primary factor.")
    else:
        add("Factor/comparator conceptual alignment", "Pass", "High", "No obvious terminology conflict was detected.", "Verify roles against the actual protocol.")

    if secondary and secondary.lower() in {factor.lower(), outcome.lower(), comparator.lower()}:
        add("Secondary factor distinctness", "Review", "Medium", "The secondary factor appears identical to another recorded role.", "Confirm that the moderator is a distinct variable rather than a duplicate field.")
    else:
        add("Secondary factor distinctness", "Pass", "Medium", "No obvious duplicate secondary factor detected.", "")

    if hypothesis and re.search(r"\b(prove|proves|guarantee|always|never)\b", hypothesis, re.I):
        add("Hypothesis claim strength", "Review", "High", "The hypothesis uses unusually absolute or proof-oriented wording.", "Use a testable association/difference statement unless the design genuinely supports the stronger claim.")
    else:
        add("Hypothesis claim strength", "Pass", "High", "No obvious absolute/proof wording detected.", "")

    if outcome and re.search(r"\b(percent|percentage|%|removal|yield|activity|concentration)\b", outcome, re.I) and not measurement:
        add("Outcome-to-measurement linkage", "Block", "Critical", "The endpoint appears quantitative, but no measurement plan is recorded.", "Specify how the endpoint will be measured and calculated before data collection.")
    else:
        add("Outcome-to-measurement linkage", "Pass", "Critical", "No obvious outcome/measurement disconnect detected.", "")

    return rows


def validation_score(rows: List[Dict[str, str]]) -> float:
    if not rows:
        return 0.0
    weights = {"Critical": 2.0, "High": 1.5, "Medium": 1.0}
    total = sum(weights.get(r["Severity"], 1.0) for r in rows)
    earned = sum(weights.get(r["Severity"], 1.0) for r in rows if r["Status"] == "Pass")
    return round(100 * earned / total, 1)


def validation_summary(rows: List[Dict[str, str]]) -> Dict[str, object]:
    score = validation_score(rows)
    blockers = [r["Check"] for r in rows if r["Status"] == "Block"]
    reviews = [r["Check"] for r in rows if r["Status"] == "Review"]
    warnings = [r["Check"] for r in rows if r["Status"] == "Warn"]
    if blockers:
        state = "Blocked"
    elif reviews or warnings:
        state = "Needs review"
    else:
        state = "Design-ready for next planning stage"
    return {"score": score, "state": state, "blockers": blockers, "reviews": reviews, "warnings": warnings}


def export_validation(plan: Dict[str, object], rows: List[Dict[str, str]], summary: Dict[str, object]) -> str:
    lines = ["# SciMantra Phase 123 — Evidence-Backed Design Validation", "", f"**Validation score:** {summary['score']}%", f"**State:** {summary['state']}", ""]
    if summary["blockers"]:
        lines += ["## Fix before proceeding", *[f"- {x}" for x in summary["blockers"]], ""]
    lines += ["## Validation checks", "", "| Check | Status | Severity | Finding | Action |", "|---|---|---|---|---|"]
    for r in rows:
        finding = r["Finding"].replace("|", "/")
        action = r["Action"].replace("|", "/")
        lines.append(f"| {r['Check']} | {r['Status']} | {r['Severity']} | {finding} | {action} |")
    lines += ["", "> Validation is a conservative planning audit. It does not establish scientific validity, causality, sample size, statistical significance, or expected results."]
    return "\n".join(lines)
