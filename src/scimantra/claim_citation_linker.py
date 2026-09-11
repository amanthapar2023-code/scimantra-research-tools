"""Claim-to-citation linkage and support audit for SciMantra Research OS."""
from __future__ import annotations
from typing import Any

STATUSES = ["Supported", "Partially supported", "Unlinked claim", "Citation missing", "Needs verification"]

def link_claim(claim_id: str, claim: str, citation_ids: list[str], evidence_ids: list[str] | None = None) -> dict[str, Any]:
    return {"claim_id": claim_id, "claim": claim.strip(), "citation_ids": citation_ids, "evidence_ids": evidence_ids or [], "status": "Supported" if citation_ids else "Unlinked claim"}

def audit_links(claims: list[dict[str, Any]], citations: list[dict[str, Any]]) -> dict[str, Any]:
    known = {str(c.get("id", "")).strip() for c in citations if str(c.get("id", "")).strip()}
    rows=[]
    for claim in claims:
        ids=[str(x).strip() for x in claim.get("citation_ids", []) if str(x).strip()]
        missing=[x for x in ids if x not in known]
        status="Unlinked claim" if not ids else ("Needs verification" if missing else "Supported")
        rows.append({"claim_id":claim.get("claim_id",""),"claim":claim.get("claim",""),"citations":ids,"missing_citations":missing,"status":status})
    unlinked=sum(x["status"]=="Unlinked claim" for x in rows)
    broken=sum(bool(x["missing_citations"]) for x in rows)
    return {"rows":rows,"claims":len(rows),"unlinked":unlinked,"broken_links":broken,"coverage":round((len(rows)-unlinked)/len(rows)*100,1) if rows else 0}

def export_markdown(audit: dict[str, Any]) -> str:
    lines=["# Claim-to-Citation Link Audit","",f"Citation coverage: {audit.get('coverage',0)}%","", "| Claim ID | Status | Citations |", "|---|---|---|"]
    for r in audit.get("rows",[]): lines.append(f"| {r.get('claim_id','')} | {r.get('status','')} | {', '.join(r.get('citations',[])) or '—'} |")
    return "\n".join(lines)
