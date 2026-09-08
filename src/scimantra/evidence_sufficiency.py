"""Evidence Sufficiency Engine for manuscript claims."""
from __future__ import annotations
from typing import Any

STATUSES = ["Supported", "Partially supported", "Insufficient evidence", "Contradictory evidence", "Not assessed"]
EVIDENCE_TYPES = ["Primary dataset", "Statistical analysis", "Figure/Table", "Experimental method", "Literature", "Multiple sources", "Other"]

def assess_claim(claim: str, evidence: str = "", evidence_type: str = "", support: str = "Not assessed", design: str = "", robustness: str = "Not assessed", provenance: str = "") -> dict[str, Any]:
    claim = str(claim or "").strip()
    evidence = str(evidence or "").strip()
    design = str(design or "").strip()
    provenance = str(provenance or "").strip()
    issues: list[str] = []
    if not claim: issues.append("No claim supplied.")
    if not evidence: issues.append("No evidence anchor supplied.")
    if not design: issues.append("Study design / analysis context is missing.")
    if not provenance: issues.append("Evidence provenance is missing.")
    if support == "Contradicted": status = "Contradictory evidence"
    elif support == "Supported" and evidence and design and provenance and robustness in {"Stable", "Mostly stable", "Not assessed"}: status = "Supported"
    elif support == "Partially supported": status = "Partially supported"
    elif not evidence or not provenance: status = "Insufficient evidence"
    else: status = "Not assessed"
    return {"Claim": claim, "Status": status, "Evidence type": evidence_type or "Not specified", "Evidence supplied": bool(evidence), "Design supplied": bool(design), "Provenance supplied": bool(provenance), "Robustness": robustness, "Issues": issues}

def evidence_score(result: dict[str, Any]) -> float:
    base = {"Supported": 100, "Partially supported": 65, "Insufficient evidence": 25, "Contradictory evidence": 10, "Not assessed": 0}.get(result.get("Status"), 0)
    for key in ("Evidence supplied", "Design supplied", "Provenance supplied"):
        if not result.get(key): base -= 15
    if result.get("Robustness") == "Fragile": base -= 20
    elif result.get("Robustness") == "Sensitive": base -= 10
    return round(max(0, min(100, base)), 1)

def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {"claims": len(results), "supported": sum(r["Status"] == "Supported" for r in results), "partial": sum(r["Status"] == "Partially supported" for r in results), "insufficient": sum(r["Status"] == "Insufficient evidence" for r in results), "contradictory": sum(r["Status"] == "Contradictory evidence" for r in results), "not_assessed": sum(r["Status"] == "Not assessed" for r in results), "mean_score": round(sum(evidence_score(r) for r in results) / len(results), 1) if results else 0.0}

def priority_queue(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for i, r in enumerate(results, 1):
        score = evidence_score(r)
        priority = 100 - score
        action = "Resolve contradiction" if r["Status"] == "Contradictory evidence" else "Locate and verify evidence" if r["Status"] == "Insufficient evidence" else "Strengthen support and document limitations" if r["Status"] == "Partially supported" else "Verify robustness/provenance" if score < 100 else "No immediate evidence gap"
        out.append({"Priority": priority, "Claim": r["Claim"], "Status": r["Status"], "Recommended action": action})
    return sorted(out, key=lambda x: x["Priority"], reverse=True)

def export_sufficiency(results: list[dict[str, Any]], summary_data: dict[str, Any]) -> str:
    lines = ["# SciMantra Evidence Sufficiency Audit", "", f"Mean evidence-support score: {summary_data['mean_score']}/100", "", "> This is a structured audit of researcher-supplied evidence. It does not establish scientific truth or publication readiness.", ""]
    for i, r in enumerate(results, 1):
        lines += [f"## Claim {i} — {r['Status']}", r['Claim'], f"- Evidence type: {r['Evidence type']}", f"- Evidence supplied: {r['Evidence supplied']}", f"- Design supplied: {r['Design supplied']}", f"- Provenance supplied: {r['Provenance supplied']}", f"- Robustness: {r['Robustness']}", f"- Score: {evidence_score(r)}/100", ""]
    return "\n".join(lines)
