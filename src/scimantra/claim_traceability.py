"""Claim-to-evidence traceability checks for research manuscripts."""
from __future__ import annotations
import re
from typing import Any

CAUSAL = re.compile(r"\b(caused|causes|led to|resulted in|improved|reduced|increased|enhanced|demonstrates that)\b", re.I)
QUANT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|fold|mg|g|mL|µg|h|hr|days?|years?)\b", re.I)
CITATION = re.compile(r"\[[0-9,\- ]+\]|\([A-Z][A-Za-z-]+(?: et al\.)?,?\s*\d{4}\)")

def classify_claim(claim: str) -> dict[str, Any]:
    text = claim.strip()
    if not text:
        return {"claim": "", "level": "EMPTY", "flags": ["Enter a claim."]}
    flags = []
    if CAUSAL.search(text): flags.append("Causal language detected — verify design and assumptions.")
    if QUANT.search(text): flags.append("Quantitative claim — verify against the underlying dataset/table/figure.")
    if not CITATION.search(text): flags.append("No citation pattern detected — literature or source support may be required.")
    level = "CAUSAL" if CAUSAL.search(text) else "QUANTITATIVE" if QUANT.search(text) else "INTERPRETIVE"
    return {"claim": text, "level": level, "flags": flags}

def trace_claim(claim: str, evidence_location: str = "", evidence_type: str = "Not specified", support: str = "Not assessed") -> dict[str, str]:
    item = classify_claim(claim)
    return {"Claim": item["claim"], "Claim level": item["level"], "Evidence type": evidence_type, "Evidence location": evidence_location.strip() or "MISSING", "Support status": support, "Audit": " | ".join(item["flags"]) or "No automatic warning."}

def audit_claims(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    linked = sum(bool(str(r.get("Evidence location", "")).strip()) and str(r.get("Evidence location")) != "MISSING" for r in records)
    return {"total": total, "linked": linked, "unlinked": total - linked, "coverage_percent": round(100 * linked / total, 1) if total else 0.0}
