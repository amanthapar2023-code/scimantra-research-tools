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
) -> List[Dict]:
    """Generate explicit, falsifiable planning candidates from user-defined variables.

    The engine deliberately refuses placeholder variables and does not invent effect
    sizes or expected results. The directional statement is phrased as a contrast
    when a comparator is supplied, while the null states the corresponding absence
    of evidence under the pre-specified analysis.
    """
    q = _clean(question.get("Research question", ""))
    factor = _label(primary_variable, "the primary factor")
    endpoint = _label(outcome, "the primary outcome")
    reference = _clean(comparator)

    if reference:
        directional = (
            f"Under the defined study conditions, changing {factor} will be associated "
            f"with a difference in {endpoint} compared with {reference}."
        )
        null = (
            f"Under the defined study conditions, changing {factor} will not be associated "
            f"with a difference in {endpoint} compared with {reference}."
        )
        directional_falsifier = (
            f"The pre-specified analysis shows no difference in {endpoint} between the "
            f"defined {factor} conditions and {reference}, within the study's decision criteria."
        )
        null_falsifier = (
            f"The pre-specified analysis shows a difference in {endpoint} between the "
            f"defined {factor} conditions and {reference}, meeting the study's decision criteria."
        )
    else:
        directional = (
            f"Under the defined study conditions, changing {factor} will be associated "
            f"with a difference in {endpoint}."
        )
        null = (
            f"Under the defined study conditions, changing {factor} will not be associated "
            f"with a difference in {endpoint}."
        )
        directional_falsifier = (
            f"The pre-specified analysis shows no difference in {endpoint} across the defined {factor} conditions."
        )
        null_falsifier = (
            f"The pre-specified analysis shows a difference in {endpoint} across the defined {factor} conditions, meeting the study's decision criteria."
        )

    # Interaction is only meaningful if the researcher identifies a second factor or context.
    interaction = (
        f"The association between {factor} and {endpoint} will differ across a pre-specified "
        "second factor or experimental context."
    )

    return [
        {"Level": "Directional", "Hypothesis": directional, "Falsifier": directional_falsifier},
        {"Level": "Null", "Hypothesis": null, "Falsifier": null_falsifier},
        {
            "Level": "Interaction",
            "Hypothesis": interaction,
            "Falsifier": "No credible interaction is observed under the pre-specified model and decision criteria.",
        },
    ]


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
