"""Evidence-grounded manuscript drafting primitives for SciMantra."""
from __future__ import annotations
from typing import Any

SECTIONS = ["Introduction", "Methods", "Results", "Discussion", "Conclusion"]


def draft_section(section: str, evidence: list[dict[str, Any]], claims: list[dict[str, Any]], citations: list[dict[str, Any]]) -> dict[str, Any]:
    section = section if section in SECTIONS else "Introduction"
    usable_claims = [c for c in claims if str(c.get("section", section)) == section or not c.get("section")]
    usable_evidence = [e for e in evidence if e.get("verified", False)]
    lines = [f"## {section}", "", "Evidence-grounded drafting outline:"]
    if usable_claims:
        for c in usable_claims:
            lines.append(f"- Claim: {c.get('claim','').strip()} [Evidence: {c.get('evidence_id','unlinked')}]" )
    else:
        lines.append("- Add a researcher-authored claim linked to evidence before drafting.")
    if usable_evidence:
        lines.append("", "Verified evidence anchors:")
        for e in usable_evidence[:10]: lines.append(f"- {e.get('id','')}: {e.get('statement','').strip()}")
    if citations:
        lines.append("", "Citation anchors:")
        for c in citations[:10]: lines.append(f"- {c.get('id','')}: {c.get('title','').strip()}")
    return {"section": section, "text": "\n".join(lines), "claims_used": len(usable_claims), "evidence_used": len(usable_evidence), "citations_used": len(citations)}


def audit_draft(text: str, evidence: list[dict[str, Any]], claims: list[dict[str, Any]]) -> dict[str, Any]:
    words = len(text.split()) if text.strip() else 0
    claim_ids = {str(c.get("claim", "")).strip() for c in claims if str(c.get("claim", "")).strip()}
    evidence_ids = {str(e.get("id", "")).strip() for e in evidence if str(e.get("id", "")).strip()}
    return {"word_count": words, "evidence_anchors": len(evidence_ids), "claim_records": len(claim_ids), "has_text": bool(text.strip()), "warning": "Drafting support does not establish scientific validity or guarantee citation correctness."}
