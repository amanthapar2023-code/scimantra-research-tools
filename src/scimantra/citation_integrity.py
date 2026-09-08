"""Citation and source-integrity heuristics for manuscript claims."""
from __future__ import annotations
import re
from typing import Any

CITATION_PATTERNS = [r"\([^)]{2,120},\s*\d{4}\)", r"\[[0-9,;\- ]+\]", r"doi\s*[:/]", r"https?://doi\.org/"]

def citation_present(text: str) -> bool:
    return any(re.search(p, text, re.I) for p in CITATION_PATTERNS)

def audit_claim(claim: str, source: str = "", evidence: str = "") -> dict[str, Any]:
    claim = claim.strip()
    source = source.strip()
    evidence = evidence.strip()
    causal = bool(re.search(r"\b(causes?|caused|leads? to|results? in|proves?|demonstrates? that)\b", claim, re.I))
    return {
        "Claim": claim,
        "Citation detected": citation_present(claim),
        "Source supplied": bool(source),
        "Evidence supplied": bool(evidence),
        "Potential causal wording": causal,
        "Status": "SOURCE + EVIDENCE" if source and evidence else "SOURCE NEEDED" if not source else "EVIDENCE NEEDED",
    }

def audit_manuscript_claims(claims: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(claims)
    linked = sum(bool(c.get("Source supplied") and c.get("Evidence supplied")) for c in claims)
    citations = sum(bool(c.get("Citation detected")) for c in claims)
    causal = sum(bool(c.get("Potential causal wording")) for c in claims)
    return {"total": total, "fully_linked": linked, "citation_detected": citations, "causal_flags": causal, "coverage": round(100 * linked / total, 1) if total else 0.0}

def export_audit(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "# Citation Integrity Audit\n\nNo claims recorded."
    headers = list(rows[0].keys())
    lines = ["# Citation & Source Integrity Audit", "", "This is a traceability heuristic, not a judgment of source quality or scientific truth.", "", "| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")).replace("|", "/") for h in headers) + " |")
    return "\n".join(lines)
