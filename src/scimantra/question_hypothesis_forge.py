import re
from typing import Dict, List


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().rstrip(".")


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


def generate_hypotheses(question: Dict, primary_variable: str = "the pre-specified factor", outcome: str = "the primary outcome", comparator: str = "the comparator") -> List[Dict]:
    q = _clean(question.get("Research question", ""))
    return [
        {"Level": "Directional", "Hypothesis": f"Changing {primary_variable} will be associated with a pre-specified change in {outcome} relative to {comparator}.", "Falsifier": f"No pre-specified difference is observed under the defined analysis for: {q}"},
        {"Level": "Null", "Hypothesis": f"Changing {primary_variable} will not produce a pre-specified difference in {outcome} relative to {comparator}.", "Falsifier": "A pre-specified difference meeting the study's analysis criteria is observed."},
        {"Level": "Interaction", "Hypothesis": f"The effect of {primary_variable} on {outcome} will differ across a pre-specified context or factor.", "Falsifier": "No credible interaction is observed under the pre-specified model."},
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
