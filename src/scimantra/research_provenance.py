"""Research evidence provenance vault: link claims to upstream evidence artifacts."""
from __future__ import annotations
from typing import Any

TYPES = ["Raw evidence", "Dataset", "Analysis", "Result", "Figure", "Table", "Claim", "Manuscript sentence", "Literature source", "Protocol / method"]
STATUSES = ["Not assessed", "Verified", "Partially verified", "Needs source", "Needs verification"]

def template():
    return [{"ID": f"P{i:03d}", "Type": t, "Title / statement": "", "Parent ID": "", "Source / location": "", "Status": "Not assessed", "Notes": ""} for i, t in enumerate(TYPES, 1)]

def audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [str(r.get("ID", "")).strip() for r in rows]
    dup = sorted({x for x in ids if x and ids.count(x) > 1})
    missing_parent = [r.get("ID", "") for r in rows if r.get("Type") not in {"Raw evidence", "Literature source", "Protocol / method"} and not str(r.get("Parent ID", "")).strip()]
    needs = [r.get("ID", "") for r in rows if r.get("Status") in {"Needs source", "Needs verification", "Not assessed"}]
    known = set(ids)
    broken = [r.get("ID", "") for r in rows if str(r.get("Parent ID", "")).strip() and r.get("Parent ID") not in known]
    verified = sum(r.get("Status") == "Verified" for r in rows)
    return {"records": len(rows), "verified": verified, "unresolved": len(needs), "duplicate_ids": dup, "missing_parent": missing_parent, "broken_links": broken, "coverage": round(100 * verified / len(rows), 1) if rows else 0}

def provenance_queue(rows):
    rank = {"Needs source": 100, "Needs verification": 90, "Not assessed": 70, "Partially verified": 45, "Verified": 0}
    return sorted([{"Priority": rank.get(r.get("Status"), 70), "ID": r.get("ID", ""), "Type": r.get("Type", ""), "Status": r.get("Status", ""), "Action": "Add/verify upstream source or parent link" if r.get("Status") != "Verified" else "Retain source trace"} for r in rows], key=lambda x: x["Priority"], reverse=True)

def trace_sentence(sentence_id: str, rows):
    by_id = {str(r.get("ID")): r for r in rows}
    chain, seen = [], set()
    current = sentence_id
    while current and current in by_id and current not in seen:
        seen.add(current); r = by_id[current]; chain.append(r); current = str(r.get("Parent ID", "")).strip()
    return chain

def export_vault(rows, summary):
    lines = ["# SciMantra Research Evidence Provenance Vault", "", f"Verified coverage: {summary['coverage']}%", "> Provenance records document researcher-supplied source relationships; they do not certify data authenticity or scientific correctness.", ""]
    for r in rows:
        lines += [f"## {r.get('ID','')} — {r.get('Type','')}", f"- Statement: {r.get('Title / statement','')}", f"- Parent: {r.get('Parent ID','')}", f"- Source/location: {r.get('Source / location','')}", f"- Status: {r.get('Status','')}", ""]
    return "\n".join(lines)
