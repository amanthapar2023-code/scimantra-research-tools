"""Structured manuscript workspace with evidence-aware section prompts."""
from __future__ import annotations
from typing import Any

SECTIONS = ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion", "References"]

PROMPTS = {
    "Title": "State the study system, approach and primary outcome without overstating causality.",
    "Abstract": "Summarize background, objective, methods, key observed results and conclusion using only verified evidence.",
    "Introduction": "Move from established context to the unresolved problem, literature gap, study question and contribution.",
    "Methods": "Document design, experimental unit, controls, replication, measurements, analysis and reproducibility details.",
    "Results": "Report observed data and analyses clearly; separate description from interpretation.",
    "Discussion": "Interpret findings against the research question and literature, test alternatives, acknowledge limitations and define implications.",
    "Conclusion": "State only conclusions supported by the documented evidence and identify the most defensible next step.",
    "References": "Record complete source metadata and ensure cited claims have traceable evidence."
}

def section_template(title: str = "") -> dict[str, dict[str, Any]]:
    return {s: {"draft": "", "evidence": "", "status": "Not started", "prompt": PROMPTS[s]} for s in SECTIONS}

def audit_sections(workspace: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for section in SECTIONS:
        item = workspace.get(section, {})
        draft = str(item.get("draft", "")).strip()
        evidence = str(item.get("evidence", "")).strip()
        status = "Evidence linked" if draft and evidence else "Draft only" if draft else "Not started"
        rows.append({"Section": section, "Status": status, "Evidence linked": bool(evidence), "Draft length": len(draft)})
    return rows

def manuscript_markdown(title: str, workspace: dict[str, dict[str, Any]]) -> str:
    lines = [f"# {title or 'Research Manuscript'}", "", "Evidence-aware manuscript workspace export. Verify every claim before submission.", ""]
    for section in SECTIONS:
        item = workspace.get(section, {})
        lines += [f"## {section}", "", item.get("draft", ""), "", f"**Evidence / source notes:** {item.get('evidence','')}", ""]
    return "\n".join(lines)
