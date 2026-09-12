import re
from typing import Dict, List


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().rstrip(".")


def _label(text: str, fallback: str) -> str:
    value = _clean(text)
    return value if value else fallback


def _context_from_gap(gap_text: str, research_title: str) -> str:
    gap = _clean(gap_text)
    title = _clean(research_title)
    if gap and title:
        return f"{title}; specifically, {gap.lower()}"
    return title or gap or "the target research context"


def generate_questions(gap: Dict, research_title: str = "") -> List[Dict]:
    gap_text = _clean(gap.get("Candidate research question", ""))
    dimension = _clean(gap.get("Gap dimension", "the unresolved area")).lower()
    context = _context_from_gap(gap_text, research_title)
    focus = gap_text or f"the {dimension}"
    return [
        {"Type": "Descriptive", "Research question": f"What is currently unresolved about {focus} in {context}?", "Purpose": "Define the unresolved state before testing an explanation."},
        {"Type": "Comparative", "Research question": f"How does the proposed approach compare with an appropriate reference condition for {focus} in {context}?", "Purpose": "Create an explicit comparator and measurable distinction."},
        {"Type": "Mechanistic", "Research question": f"Which measurable factors could explain differences in the primary outcome related to {focus} in {context}?", "Purpose": "Generate explanatory candidates without assuming causality."},
        {"Type": "Intervention / experimental", "Research question": f"Does the pre-specified intervention or exposure change the primary measurable outcome compared with an appropriate reference condition in {context}, and does that effect vary across a defined secondary factor when relevant?", "Purpose": "Convert the gap into a falsifiable experimental question."},
        {"Type": "Robustness", "Research question": f"Does the proposed relationship for {focus} remain under alternative controls, conditions, or analysis assumptions in {context}?", "Purpose": "Test sensitivity to assumptions and alternative explanations."},
    ]


def generate_hypotheses(
    question: Dict,
    primary_variable: str = "",
    outcome: str = "",
    comparator: str = "",
    secondary_factor: str = "",
    system: str = "",
    conditions: str = "",
    direction: str = "Non-directional",
    direction_basis: str = "",
) -> List[Dict]:
    """Generate explicit, falsifiable planning candidates from researcher-defined variables.

    Directional language is used only when the researcher selects an evidence-supported
    direction and records a basis. Otherwise the primary hypothesis remains non-directional.
    """
    factor = _label(primary_variable, "the primary factor")
    endpoint = _label(outcome, "the primary outcome")
    reference = _clean(comparator)
    secondary = _clean(secondary_factor)
    context = _clean(conditions) or _clean(system) or "the defined study conditions"
    prefix = f"Under {context}, "
    direction = _clean(direction).lower()
    basis = _clean(direction_basis)

    if reference:
        comparison = f"compared with {reference}"
        if direction == "higher":
            primary = f"{prefix}{factor} will result in higher {endpoint} {comparison}."
        elif direction == "lower":
            primary = f"{prefix}{factor} will result in lower {endpoint} {comparison}."
        else:
            primary = f"{prefix}{factor} will be associated with a difference in {endpoint} {comparison}."
        null = f"{prefix}{factor} will not be associated with a difference in {endpoint} {comparison}."
        primary_falsifier = f"The pre-specified analysis does not show the stated difference in {endpoint} {comparison}, within the study's decision criteria."
        null_falsifier = f"The pre-specified analysis shows a difference in {endpoint} {comparison}, meeting the study's decision criteria."
    else:
        if direction == "higher":
            primary = f"{prefix}{factor} will result in higher {endpoint}."
        elif direction == "lower":
            primary = f"{prefix}{factor} will result in lower {endpoint}."
        else:
            primary = f"{prefix}{factor} will be associated with a difference in {endpoint}."
        null = f"{prefix}{factor} will not be associated with a difference in {endpoint}."
        primary_falsifier = f"The pre-specified analysis does not show the stated difference in {endpoint} across the defined {factor} conditions."
        null_falsifier = f"The pre-specified analysis shows a difference in {endpoint} across the defined {factor} conditions, meeting the study's decision criteria."

    if secondary:
        interaction = f"The effect of {factor} on {endpoint} will differ across levels of {secondary}."
        interaction_falsifier = f"No credible {factor} × {secondary} interaction is observed under the pre-specified model and decision criteria."
    else:
        interaction = f"The effect of {factor} on {endpoint} will differ across a pre-specified second factor or experimental context."
        interaction_falsifier = "No credible interaction is observed under the pre-specified model and decision criteria."

    basis_note = basis if basis else "No directional evidence basis recorded; the primary hypothesis is therefore treated as non-directional."
    return [
        {"Level": "Primary", "Hypothesis": primary, "Falsifier": primary_falsifier, "Evidence basis": basis_note},
        {"Level": "Null", "Hypothesis": null, "Falsifier": null_falsifier, "Evidence basis": "Logical counterpart of the primary hypothesis; not an expected result."},
        {"Level": "Interaction", "Hypothesis": interaction, "Falsifier": interaction_falsifier, "Evidence basis": "Requires a pre-specified moderator and interaction model."},
    ]


def audit_design(primary_variable: str, outcome: str, comparator: str, secondary_factor: str = "", system: str = "", conditions: str = "") -> List[Dict]:
    """Audit whether the supplied roles form a coherent experimental specification."""
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
        checks.append({"Check": "Factor–comparator role consistency", "Status": "Review", "Finding": "The primary factor looks like a dose/exposure variable while the comparator looks like a treatment/control condition. Consider defining the treatment as the primary intervention and the dose/exposure as a secondary factor, unless the design intentionally tests both dimensions."})
    else:
        checks.append({"Check": "Factor–comparator role consistency", "Status": "No obvious mismatch", "Finding": "Roles appear compatible from the supplied labels; verify against the actual study design."})
    return checks


def audit_question(question: str) -> List[Dict]:
    q = _clean(question)
    return [
        {"Check": "Specific population/context", "Status": "Present" if len(q.split()) >= 8 else "Needs detail", "Prompt": "Define the system, population, setting, or experimental conditions."},
        {"Check": "Measurable outcome", "Status": "Present" if re.search(r"outcome|measure|change|difference|effect|associated", q, re.I) else "Needs detail", "Prompt": "Name the primary measurable endpoint."},
        {"Check": "Comparator", "Status": "Present" if re.search(r"compar|versus|relative|against|reference", q, re.I) else "Needs detail", "Prompt": "Specify the comparator or reference condition."},
        {"Check": "Falsifiability", "Status": "Present" if re.search(r"does|how|which|what", q, re.I) else "Needs detail", "Prompt": "State what observation would count against the proposed explanation."},
        {"Check": "Causal wording", "Status": "Review" if re.search(r"cause|prove|lead to", q, re.I) else "OK", "Prompt": "Use causal language only when the design can support it."},
    ]


def audit_direction(direction: str, basis: str) -> List[Dict]:
    selected = _clean(direction).lower()
    evidence = _clean(basis)
    if selected in {"higher", "lower"} and not evidence:
        return [{"Check": "Directional evidence basis", "Status": "Needs detail", "Finding": "A higher/lower directional hypothesis was selected without recording the evidence basis. Add the literature or rationale that justifies the direction, or use Non-directional."}]
    if selected == "non-directional":
        return [{"Check": "Directional evidence basis", "Status": "Not required", "Finding": "No directional expectation is being asserted. The primary hypothesis will test for a difference without predicting its sign."}]
    return [{"Check": "Directional evidence basis", "Status": "Present", "Finding": evidence}]


def export_forge(questions: List[Dict], hypotheses: List[Dict]) -> str:
    lines = ["# SciMantra Research Question & Hypothesis Forge", "", "## Research questions"]
    for i, q in enumerate(questions, 1):
        lines += [f"### {i}. {q['Type']}", f"**Question:** {q['Research question']}", f"**Purpose:** {q['Purpose']}", ""]
    lines += ["## Hypotheses"]
    for h in hypotheses:
        lines += [f"### {h['Level']}", f"**Hypothesis:** {h['Hypothesis']}", f"**Falsifier:** {h['Falsifier']}", f"**Evidence basis:** {h.get('Evidence basis', '')}", ""]
    lines.append("> These are planning candidates. They do not establish a scientific relationship or predicted result.")
    return "\n".join(lines)
