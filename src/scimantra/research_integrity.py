"""Transparent research-integrity and contradiction audit helpers."""
from __future__ import annotations
import re
from typing import Any

RECORD_TYPES = ["Manuscript claim", "Result", "Figure", "Table", "Analysis", "Literature finding", "Method / protocol"]
DIRECTIONS = ["Not assessed", "Increases / positive", "Decreases / negative", "No difference / null", "Mixed / conditional"]


def default_records() -> list[dict[str, Any]]:
    return [{"ID": f"R{i}", "Type": t, "Topic": "Primary outcome", "Statement": "", "Value": "", "Unit": "", "Direction": "Not assessed", "Source": "", "Status": "Unverified", "Notes": ""} for i, t in enumerate(["Manuscript claim", "Result", "Figure"], 1)]


def _num(value: Any) -> float | None:
    m = re.search(r"[-+]?\d+(?:\.\d+)?", str(value or ""))
    return float(m.group()) if m else None


def audit_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    ids = [str(r.get("ID", "")).strip() for r in records]
    for dup in sorted({x for x in ids if x and ids.count(x) > 1}):
        issues.append({"Severity":"High","Type":"Duplicate ID","Records":dup,"Problem":"The same record ID is used more than once.","Action":"Assign a unique ID."})
    for r in records:
        rid = str(r.get("ID", "?")).strip() or "?"
        if not str(r.get("Statement", "")).strip():
            issues.append({"Severity":"Moderate","Type":"Missing statement","Records":rid,"Problem":"No auditable statement was entered.","Action":"Enter the exact researcher-verified statement."})
        if not str(r.get("Source", "")).strip():
            issues.append({"Severity":"Moderate","Type":"Missing source","Records":rid,"Problem":"No evidence/source anchor is attached.","Action":"Attach the dataset, analysis, figure/table, protocol or literature location."})
        if str(r.get("Status", "")) not in {"Verified", "Researcher confirmed"}:
            issues.append({"Severity":"Low","Type":"Verification pending","Records":rid,"Problem":"The record is not marked verified.","Action":"Check against the original evidence."})
    topics: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        topic = str(r.get("Topic", "")).strip().lower()
        if topic: topics.setdefault(topic, []).append(r)
    for topic, group in topics.items():
        dirs = {str(r.get("Direction", "")) for r in group}
        if "Increases / positive" in dirs and "Decreases / negative" in dirs:
            ids2 = ", ".join(str(r.get("ID", "?")) for r in group)
            issues.append({"Severity":"High","Type":"Direction conflict","Records":ids2,"Problem":f"Topic '{topic}' contains opposite directional statements.","Action":"Inspect the authoritative data and determine whether the difference is genuine, conditional, subgroup-specific, or an error."})
        numeric = [(str(r.get("ID","?")), _num(r.get("Value")), str(r.get("Unit","")).strip().lower()) for r in group]
        for i, v, u in numeric:
            for j, w, u2 in numeric:
                if i < j and v is not None and w is not None and u and u == u2 and v != w:
                    issues.append({"Severity":"High","Type":"Numeric mismatch","Records":f"{i}, {j}","Problem":f"Same-topic records report {v:g} versus {w:g} {u}.","Action":"Reconcile with the authoritative analysis output; check rounding, denominators, transformations and subgroup definitions."})
    claims = [r for r in records if str(r.get("Type", "")) == "Manuscript claim"]
    summary = {"records":len(records),"issues":len(issues),"high":sum(x["Severity"]=="High" for x in issues),"moderate":sum(x["Severity"]=="Moderate" for x in issues),"low":sum(x["Severity"]=="Low" for x in issues),"claims":len(claims),"unanchored_claims":sum(not str(r.get("Source","")).strip() for r in claims)}
    return {"issues":issues,"summary":summary}


def consistency_score(audit: dict[str, Any]) -> float:
    s = audit.get("summary", {})
    if not s.get("records"): return 0.0
    penalty = 20*int(s.get("high",0)) + 8*int(s.get("moderate",0)) + 2*int(s.get("low",0))
    return round(max(0.0, min(100.0, 100-penalty)), 1)


def export_integrity(records: list[dict[str, Any]], audit: dict[str, Any]) -> str:
    lines = ["# Research Integrity & Contradiction Audit", "", f"Consistency score (planning heuristic): {consistency_score(audit)}%", "> Flags are prompts for researcher verification; they do not determine scientific truth.", ""]
    for x in audit.get("issues", []): lines += [f"## {x['Severity']} — {x['Type']}", f"- Records: {x['Records']}", f"- Problem: {x['Problem']}", f"- Action: {x['Action']}", ""]
    lines += ["## Records"] + [f"- `{r.get('ID','')}` [{r.get('Type','')}] {r.get('Topic','')}: {r.get('Statement','')} | source: {r.get('Source','')}" for r in records]
    return "\n".join(lines)
