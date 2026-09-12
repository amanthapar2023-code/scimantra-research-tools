import re
from typing import Dict, List


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().rstrip(".")


def _label(text: str, fallback: str) -> str:
    value = _clean(text)
    return value if value else fallback


def generate_questions(gap: Dict, research_title: str = "") -> List[Dict]:
    dim = _clean(gap.get("Gap dimension", "the unresolved area")).lower()
    context = _clean(research_title) or "the target research context"
    return [
        {"Type": "Descriptive", "Research question": f"What remains unresolved about {dim} in {context}?", "Purpose": "Precisely define the unresolved state before testing an explanation."},
        {"Type": "Comparative", "Research question": f"How does the proposed approach differ from relevant alternatives for {dim} in {context}?", "Purpose": "Create an explicit comparator and measurable distinction."},
        {"Type": "Mechanistic", "Research question": f"Which measurable factors could explain differences observed in {dim} within {context}?", "Purpose": "Generate testable explanatory candidates without assuming causality."},
        {"Type": "Intervention / experimental", "Research question": f"Does changing a pre-specified factor alter the primary outcome related to {dim} under defined conditions in {context}?", "Purpose": "Convert the gap into a falsifiable experiment."},
        {"Type": "Robustness", "Research question": f"Does the proposed relationship for {dim} remain under alternative conditions, controls, or analyses?", "Purpose": "Test whether the finding is sensitive to assumptions."},
    ]


def generate_hypotheses(
    question: Dict,
    primary_variable: str = "",
    outcome: str = "",
    comparator: str = "",
    secondary_factor: str = "",
    system: str = "",
    conditions: str = "",
) -> List[Dict]:
    """Generate explicit, falsifiable planning candidates from researcher-defined variables."""
    factor = _label(primary_variable, "the primary factor")
    endpoint = _label(outcome, "the primary outcome")
    reference = _clean(comparator)
    context = _clean(conditions) or _clean(system) or "the defined study conditions"

    prefix = f"Under {context}, "
    if reference:
        directional = f"{prefix}changing {factor} will be associated with a difference in {endpoint} compared with {reference}."
        null = f"{prefix}changing {factor} will not be associated with a difference in {endpoint} compared with {reference}."
        directional_falsifier = f"The pre-specified analysis shows no difference in {endpoint} between the defined {factor} conditions and {reference}, within the study's decision criteria."
        null_falsifier = f"The pre-specified analysis shows a difference in {endpoint} between the defined {factor} conditions and {reference}, meeting the study's decision criteria."
    else:
        directional = f"{prefix}changing {factor} will be associated with a difference in {endpoint}."
        null = f"{prefix}changing {factor} will not be associated with a difference in {endpoint}."
        directional_falsifier = f"The pre-specified analysis shows no difference in {endpoint} across the defined {factor} conditions."
        null_falsifier = f"The pre-specified analysis shows a difference in {endpoint} across the defined {factor} conditions, meeting the study's decision criteria."

    if secondary_factor:
        interaction = f"The association between {factor} and {endpoint} will differ across the pre-specified secondary factor, {secondary_factor}."
    else:
        interaction = f"The association between {factor} and {endpoint} will differ across a pre-specified second factor or experimental context."

    return [
        {"Level": "Directional", "Hypothesis": directional, "Falsifier": directional_falsifier},
        {"Level": "Null", "Hypothesis": null, "Falsifier": null_falsifier},
        {"Level": "Interaction", "Hypothesis": interaction, "Falsifier": "No credible interaction is observed under the pre-specified model and decision criteria."},
    ]


def audit_design(primary_variable: str, outcome: str, comparator: str, secondary_factor: str = "", system: str = "", conditions: str = "") -> List[Dict]:
    """Audit whether the supplied roles form a coherent experimental specification.

    This is a planning audit, not a scientific validity claim. It flags common role
    mismatches, especially when a treatment-style comparator is paired with a dose
    or exposure variable without identifying the treatment as a separate factor.
    """
    factor = _clean(primary_variable)
    comp = _clean(comparator)
    secondary = _clean(secondary_factor)
    checks: List[Dict] = []

    if not factor:
        checks.append({"Check": "Primary intervention / exposure", "Status": "Needs detail", "Finding": "Define what is manipulated, assigned, measured, or compared as the primary factor."})
    else:
        checks.append({"Check": "Primary intervention / exposure", "Status": "Present", "Finding": factor})

    if not _clean(outcome):
        checks.append({"Check": "Primary outcome", "Status": "Needs detail", "Finding": "Name the measurable primary endpoint."})
    else:
        checks.append({"Check": "Primary outcome", "Status": "Present", "Finding": _clean(outcome)})

    if not comp:
        checks.append({"Check": "Comparator", "Status": "Optional", "Finding": "No comparator supplied; add one when the study has a reference condition."})
    else:
        checks.append({"Check": "Comparator", "Status": "Present", "Finding": comp})

    if secondary:
        checks.append({"Check": "Secondary factor / moderator", "Status": "Present", "Finding": secondary})
    else:
        checks.append({"Check": "Secondary factor / moderator", "Status": "Optional", "Finding": "Add a second factor when testing dose-response, moderation, or interaction."})

    if not _clean(system):
        checks.append({"Check": "Population / system", "Status": "Needs detail", "Finding": "Define the biological system, population, material, or experimental unit."})
    else:
        checks.append({"Check": "Population / system", "Status": "Present", "Finding": _clean(system)})

    if not _clean(conditions):
        checks.append({"Check": "Experimental conditions", "Status": "Needs detail", "Finding": "Specify important environmental, temporal, dose, or protocol conditions."})
    else:
        checks.append({"Check": "Experimental conditions", "Status": "Present", "Finding": _clean(conditions)})

    treatment_words = r"\b(treatment|control|abiotic|biotic|microbial|untreated|vehicle|placebo)\b"
    dose_words = r"\b(concentration|dose|level|exposure|intensity|amount|ppm|mg/?l|mg/kg)\b"
    if comp and re.search(treatment_words, comp, re.I) and re.search(dose_words, factor, re.I):
        checks.append({
            "Check": "Factor–comparator role consistency",
            "Status": "Review",
            "Finding": "The primary factor looks like a dose/exposure variable while the comparator looks like a treatment/control condition. Consider defining the treatment as the primary intervention and the dose/exposure as a secondary factor, unless the design intentionally tests both dimensions."
        })
    else:
        checks.append({"Check": "Factor–comparator role consistency", "Status": "No obvious mismatch", "Finding": "Roles appear compatible from the supplied labels; verify against the actual study design."})
    return checks


def audit_question(question: str) -> List[Dict]:
    q = _clean(question)
    return [
        {"Check": "Specific population/context", "Status": "Present" if len(q.split()) >= 8 else "Needs detail", "Prompt": "Define the system, population, setting, or experimental conditions."},
        {"Check": "Measurable outcome", "Status": "Present" if re.search(r"outcome|measure|change|difference|effect|associated", q, re.I) else "Needs detail", "Prompt": "Name the primary measurable endpoint."},
        {"Check": "Comparator", "Status": "Present" if re.search(r"compar|versus|relative|against", q, re.I) else "Needs detail", "Prompt": "Specify the comparator or reference condition."},
        {"Check": "Falsifiability", "Status": "Present" if re.search(r"does|how|which|what", q, re.I) else "Needs detail", "Prompt": "State what observation would count against the proposed explanation."},
        {"Check": "Causal wording", "Status": "Review" if re.search(r"cause|prove|lead to", q, re.I) else "OK", "Prompt": "Use causal language only when the design can support it."},
    ]


def export_forge(questions: List[Dict], hypotheses: List[Dict]) -> str:
    lines = ["# SciMantra Research Question & Hypothesis Forge", "", "## Research questions"]
    for i, q in enumerate(questions, 1):
        lines += [f"### {i}. {q['Type']}", f"**Question:** {q['Research question']}", f"**Purpose:** {q['Purpose']}", ""]
    lines += ["## Hypotheses"]
    for h in hypotheses:
        lines += [f"### {h['Level']}", f"**Hypothesis:** {h['Hypothesis']}", f"**Falsifier:** {h['Falsifier']}", ""]
    lines.append("> These are planning candidates. They do not establish a scientific relationship or predicted result.")
    return "\n".join(lines)
