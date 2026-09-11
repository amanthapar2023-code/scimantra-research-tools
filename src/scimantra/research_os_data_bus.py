"""Phase 102: canonical in-session data bus for the SciMantra Research OS.

The bus gives Research OS tools one explicit project context while remaining
storage-agnostic. It is a coordination layer, not a scientific validity engine.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from typing import Any

from .research_os_state import new_project, normalize_project, progress
from .cross_tool_linkage import ensure_bus as ensure_link_bus, register_artifact as link_register_artifact, link_artifacts as link_artifacts_graph, audit_bus as audit_link_bus

SCHEMA_VERSION = 1

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_bus(project: dict[str, Any] | None = None) -> dict[str, Any]:
    p = normalize_project(project) if project else new_project()
    return {"schema_version": SCHEMA_VERSION, "project": p, "artifacts": [], "links": [], "events": [], "provenance": [], "context": {}, "created_at": _now(), "updated_at": _now()}

def ensure_bus(bus: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(bus, dict):
        return new_bus()
    out = deepcopy(bus)
    base = new_bus()
    for key in ("artifacts", "links", "events", "provenance"):
        if not isinstance(out.get(key), list): out[key] = []
    if not isinstance(out.get("context"), dict): out["context"] = {}
    out["project"] = normalize_project(out.get("project"))
    out["schema_version"] = SCHEMA_VERSION
    out.setdefault("created_at", _now()); out["updated_at"] = _now()
    return out

def upsert_project(bus: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    out = ensure_bus(bus); out["project"] = normalize_project(project); out["updated_at"] = _now(); return out

def register_artifact(bus: dict[str, Any], artifact_id: str, title: str, artifact_type: str = "Other", stage: str = "", source_tool: str = "", location: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    out = ensure_bus(bus); ident = artifact_id.strip(); clean = title.strip()
    if not ident or not clean: raise ValueError("artifact_id and title are required")
    existing = next((a for a in out["artifacts"] if a.get("id") == ident), None)
    record = {"id": ident, "title": clean, "type": artifact_type.strip() or "Other", "stage": stage.strip(), "source_tool": source_tool.strip(), "location": location.strip(), "metadata": metadata or {}, "updated_at": _now()}
    if existing: existing.update(record)
    else: out["artifacts"].append({**record, "created_at": _now()})
    out["updated_at"] = _now(); return out

def link_artifacts(bus: dict[str, Any], source_id: str, target_id: str, link_type: str = "supports", note: str = "") -> dict[str, Any]:
    out = ensure_bus(bus)
    ids = {a.get("id") for a in out["artifacts"]}
    if source_id not in ids or target_id not in ids: raise ValueError("Both artifacts must be registered on the bus before linking")
    graph = ensure_link_bus({"artifacts": out["artifacts"], "links": out["links"]})
    graph = link_register_artifact(graph, source_id, {"title": next(a["title"] for a in out["artifacts"] if a["id"] == source_id)})
    graph = link_register_artifact(graph, target_id, {"title": next(a["title"] for a in out["artifacts"] if a["id"] == target_id)})
    graph = link_artifacts_graph(graph, source_id, target_id, link_type, note)
    out["links"] = graph.get("links", out["links"])
    out["updated_at"] = _now(); return out

def record_event(bus: dict[str, Any], actor: str, action: str, entity_id: str = "", entity_type: str = "", details: str = "") -> dict[str, Any]:
    out = ensure_bus(bus)
    out["events"].append({"timestamp": _now(), "actor": actor.strip() or "Researcher", "action": action.strip() or "Updated", "entity_id": entity_id.strip(), "entity_type": entity_type.strip(), "details": details.strip()})
    out["updated_at"] = _now(); return out

def attach_provenance(bus: dict[str, Any], artifact_id: str, source: str = "", parent_id: str = "", status: str = "Not assessed", note: str = "") -> dict[str, Any]:
    out = ensure_bus(bus)
    if artifact_id not in {a.get("id") for a in out["artifacts"]}: raise ValueError("Artifact must be registered before provenance is attached")
    row = {"artifact_id": artifact_id, "source": source.strip(), "parent_id": parent_id.strip(), "status": status, "note": note.strip(), "updated_at": _now()}
    old = next((x for x in out["provenance"] if x.get("artifact_id") == artifact_id), None)
    if old: old.update(row)
    else: out["provenance"].append(row)
    out["updated_at"] = _now(); return out

def audit_bus(bus: dict[str, Any]) -> dict[str, Any]:
    out = ensure_bus(bus); ids = [a.get("id") for a in out["artifacts"]]
    duplicates = sorted({x for x in ids if ids.count(x) > 1 and x})
    link_issues = []
    for link in out["links"]:
        if link.get("source_id") not in ids or link.get("target_id") not in ids: link_issues.append(link)
    prov_issues = [p for p in out["provenance"] if p.get("artifact_id") not in ids or (p.get("parent_id") and p.get("parent_id") not in ids)]
    return {"artifact_count": len(out["artifacts"]), "link_count": len(out["links"]), "event_count": len(out["events"]), "provenance_count": len(out["provenance"]), "duplicate_artifact_ids": duplicates, "broken_links": link_issues, "broken_provenance": prov_issues, "stage_progress": progress(out["project"]), "healthy": not duplicates and not link_issues and not prov_issues}

def snapshot(bus: dict[str, Any]) -> str:
    return json.dumps(ensure_bus(bus), indent=2, ensure_ascii=False)

def load_snapshot(text: str) -> dict[str, Any]:
    try: value = json.loads(text)
    except json.JSONDecodeError as exc: raise ValueError("Invalid Research OS Data Bus JSON") from exc
    return ensure_bus(value)

def summary(bus: dict[str, Any]) -> dict[str, Any]:
    a = audit_bus(bus); return {"artifacts": a["artifact_count"], "links": a["link_count"], "events": a["event_count"], "provenance": a["provenance_count"], "complete_stages": a["stage_progress"]["complete"], "blocked_stages": a["stage_progress"]["blocked"], "healthy": a["healthy"]}
