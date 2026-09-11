"""Research Copilot 2.0: transparent project-aware research guidance."""
from __future__ import annotations
from typing import Any
from .research_workflow_automation import plan

def answer(question: str, project: dict[str, Any], audits: dict[str, Any] | None = None) -> dict[str, Any]:
    q=question.strip().lower(); actions=plan(project,audits); stages=project.get("stages",{})
    blockers=[k for k,v in stages.items() if isinstance(v,dict) and v.get("status")=="Blocked"]
    if not q: text="Ask about your research question, evidence, design, claims, manuscript, or next action."
    elif any(x in q for x in ["next","do now","what should"]): text=(actions[0]["title"]+". "+actions[0]["reason"]) if actions else "No outstanding automated action was identified."
    elif any(x in q for x in ["weak","problem","risk"]): text=("The strongest current workflow risks are: "+"; ".join(a["title"] for a in actions[:5])+".") if actions else "No rule-based workflow risk was detected from the current project state."
    elif "block" in q: text="Blocked stages: "+", ".join(blockers) if blockers else "No stages are explicitly marked Blocked."
    elif "evidence" in q or "support" in q:
        c=[a for a in actions if a["stage"] in ["Literature","Evidence","Claims"]]; text="Focus first on: "+"; ".join(a["title"] for a in c[:3]) if c else "No evidence-specific action is currently flagged."
    elif "manuscript" in q or "paper" in q or "write" in q:
        c=[a for a in actions if a["stage"] in ["Claims","Manuscript","Peer Review","Submission"]]; text="Writing readiness actions: "+"; ".join(a["title"] for a in c[:4]) if c else "No manuscript-related action is currently flagged."
    else: text="The current Copilot is limited to transparent project signals. Highest-priority action: "+(actions[0]["title"] if actions else "review the completed project manually")
    return {"answer":text,"actions":actions[:5],"confidence":"Decision-support signal; not scientific validation"}
