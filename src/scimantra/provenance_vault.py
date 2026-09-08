"""Evidence provenance planning and traceability helpers.

The vault records researcher-supplied relationships between evidence objects.
It does not verify that a source is authentic or that a claim is scientifically
true.
"""

from __future__ import annotations

from typing import Dict, List

OBJECT_TYPES = ["Raw dataset", "Processed dataset", "Observation", "Analysis result", "Figure", "Table", "Claim", "Manuscript sentence", "External source"]
RELATIONS = ["derived from", "supports", "summarizes", "visualizes", "cites", "documents", "contradicts", "depends on"]


def object_row() -> Dict[str, str]:
    return {"ID": "", "Type": "Claim", "Title / label": "", "Source / location": "", "Version": "", "Owner": "", "Notes": ""}


def link_row() -> Dict[str, str]:
    return {"From ID": "", "Relation": "derived from", "To ID": "", "Evidence / rationale": ""}


def audit_objects(objects: List[Dict[str, str]], links: List[Dict[str, str]]) -> Dict[str, object]:
    ids = [str(o.get("ID", "")).strip() for o in objects if str(o.get("ID", "")).strip()]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    known = set(ids)
    dangling = [l for l in links if str(l.get("From ID", "")).strip() not in known or str(l.get("To ID", "")).strip() not in known]
    linked = {str(l.get("From ID", "")).strip() for l in links} | {str(l.get("To ID", "")).strip() for l in links}
    isolated = [x for x in ids if x not in linked]
    missing_source = [str(o.get("ID")) for o in objects if str(o.get("ID", "")).strip() and not str(o.get("Source / location", "")).strip()]
    return {"objects": len(ids), "links": len(links), "duplicates": duplicates, "dangling": len(dangling), "isolated": len(isolated), "missing_source": len(missing_source), "coverage": round(100 * (len(ids) - len(isolated)) / len(ids), 1) if ids else 0.0}


def trace_claim(claim_id: str, objects: List[Dict[str, str]], links: List[Dict[str, str]]) -> List[Dict[str, str]]:
    known = {str(o.get("ID", "")): o for o in objects}
    frontier = [claim_id]
    seen = set()
    trace = []
    while frontier:
        current = frontier.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if current in known:
            trace.append(known[current])
        for link in links:
            if str(link.get("From ID", "")) == current:
                target = str(link.get("To ID", ""))
                if target and target not in seen:
                    frontier.append(target)
    return trace


def provenance_completeness(objects: List[Dict[str, str]], links: List[Dict[str, str]]) -> float:
    if not objects:
        return 0.0
    audited = audit_objects(objects, links)
    return round((audited["coverage"] * 0.6) + (100 - min(100, audited["missing_source"] / max(1, audited["objects"]) * 100)) * 0.4, 1)


def export_vault(objects: List[Dict[str, str]], links: List[Dict[str, str]]) -> str:
    audit = audit_objects(objects, links)
    lines = ["# Research Evidence Provenance Vault", "", f"Provenance completeness: {provenance_completeness(objects, links)}%", "", "## Objects"]
    for o in objects:
        lines.extend([f"### {o.get('ID','')} — {o.get('Title / label','')}", f"- Type: {o.get('Type','')}", f"- Source / location: {o.get('Source / location','')}", f"- Version: {o.get('Version','')}", f"- Owner: {o.get('Owner','')}", f"- Notes: {o.get('Notes','')}", ""])
    lines.append("## Provenance links")
    for l in links:
        lines.append(f"- `{l.get('From ID','')}` — **{l.get('Relation','')}** → `{l.get('To ID','')}` — {l.get('Evidence / rationale','')}")
    lines.extend(["", "## Audit", f"- Objects: {audit['objects']}", f"- Links: {audit['links']}", f"- Dangling links: {audit['dangling']}", f"- Isolated objects: {audit['isolated']}", f"- Missing source fields: {audit['missing_source']}"])
    return "\n".join(lines)
