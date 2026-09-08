"""Evidence-grounded sentence drafting helpers.

This module intentionally generates writing frames from supplied evidence rather
than inventing scientific findings or citations.
"""
from __future__ import annotations
from typing import Any

TYPES = ["Background", "Gap", "Objective", "Method", "Observed result", "Interpretation", "Limitation", "Conclusion"]

def draft_frame(claim_type: str, statement: str, evidence: str) -> dict[str, Any]:
    statement = statement.strip()
    evidence = evidence.strip()
    if not statement:
        return {"text": "", "status": "Missing statement"}
    if not evidence:
        return {"text": statement, "status": "Evidence needed"}
    frames = {
        "Background": f"Previous work reports that {statement}.",
        "Gap": f"However, the available evidence leaves unresolved whether {statement}.",
        "Objective": f"This study therefore evaluates {statement}.",
        "Method": f"To address this question, the study uses {statement}.",
        "Observed result": f"In the analyzed data, {statement}.",
        "Interpretation": f"Taken together with the cited evidence, these findings suggest that {statement}.",
        "Limitation": f"A limitation relevant to this claim is that {statement}.",
        "Conclusion": f"Within the scope of the documented evidence, the study concludes that {statement}.",
    }
    return {"text": frames.get(claim_type, statement), "status": "Evidence supplied", "evidence": evidence}

def audit_sentence(text: str, evidence: str) -> dict[str, Any]:
    t = text.lower()
    causal = any(w in t for w in ["causes", "caused", "leads to", "results in", "proves"])
    return {"Evidence linked": bool(evidence.strip()), "Potential causal wording": causal, "Needs researcher verification": True}

def export_entries(entries: list[dict[str, Any]]) -> str:
    lines = ["# Evidence-Grounded Writing Notes", "", "Draft frames require researcher verification before use in a manuscript.", ""]
    for e in entries:
        lines += [f"## {e.get('type','Claim')}", e.get("text", ""), f"**Evidence:** {e.get('evidence','')}", ""]
    return "\n".join(lines)
