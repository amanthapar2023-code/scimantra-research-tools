"""Cross-tool linkage primitives for the SciMantra Research OS.

The linker provides a small, explicit artifact graph that specialist tools can
write to without depending on one another. It does not silently infer that an
artifact is scientifically valid or that two records are equivalent.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

LINK_TYPES = ["derived_from", "supports", "tests", "uses", "contradicts", "revises", "cites"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_bus(bus: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(bus, dict):
        bus = {}
    return {
        "schema_version": 1,
        "artifacts": list(bus.get("artifacts", [])) if isinstance(bus.get("artifacts"), list) else [],
        "links": list(bus.get("links", [])) if isinstance(bus.get("links"), list) else [],
        "updated_at": _now(),
    }


def register_artifact(bus: dict[str, Any], artifact_id: str, title: str, artifact_type: str, stage: str, tool: str, payload: Any = None) -> dict[str, Any]:
    out = ensure_bus(bus)
    artifact_id = artifact_id.strip()
    title = title.strip()
    if not artifact_id or not title:
        raise ValueError("Artifact ID and title are required")
    existing = next((a for a in out["artifacts"] if a.get("id") == artifact_id), None)
    record = {"id": artifact_id, "title": title, "type": artifact_type.strip() or "Other", "stage": stage.strip(), "tool": tool.strip(), "payload": payload, "updated_at": _now()}
    if existing is None:
        out["artifacts"].append(record)
    else:
        existing.update(record)
    out["updated_at"] = record["updated_at"]
    return out


def link_artifacts(bus: dict[str, Any], source_id: str, target_id: str, link_type: str, note: str = "") -> dict[str, Any]:
    out = ensure_bus(bus)
    if not source_id.strip() or not target_id.strip():
        raise ValueError("Source and target artifact IDs are required")
    if link_type not in LINK_TYPES:
        raise ValueError(f"Unsupported link type: {link_type}")
    if source_id == target_id:
        raise ValueError("An artifact cannot link to itself")
    if not any(a.get("id") == source_id for a in out["artifacts"]):
        raise ValueError(f"Unknown source artifact: {source_id}")
    if not any(a.get("id") == target_id for a in out["artifacts"]):
        raise ValueError(f"Unknown target artifact: {target_id}")
    key = (source_id, target_id, link_type)
    if not any((x.get("source"), x.get("target"), x.get("type")) == key for x in out["links"]):
        out["links"].append({"source": source_id, "target": target_id, "type": link_type, "note": note.strip(), "created_at": _now()})
    out["updated_at"] = _now()
    return out


def incoming(bus: dict[str, Any], artifact_id: str) -> list[dict[str, Any]]:
    b = ensure_bus(bus)
    return [x for x in b["links"] if x.get("target") == artifact_id]


def outgoing(bus: dict[str, Any], artifact_id: str) -> list[dict[str, Any]]:
    b = ensure_bus(bus)
    return [x for x in b["links"] if x.get("source") == artifact_id]


def trace(bus: dict[str, Any], artifact_id: str, direction: str = "upstream", max_depth: int = 5) -> list[dict[str, Any]]:
    b = ensure_bus(bus)
    if direction not in {"upstream", "downstream"}:
        raise ValueError("direction must be upstream or downstream")
    by_id = {a.get("id"): a for a in b["artifacts"]}
    seen = {artifact_id}
    frontier = [(artifact_id, 0)]
    rows = []
    while frontier:
        current, depth = frontier.pop(0)
        if depth >= max_depth:
            continue
        links = incoming(b, current) if direction == "upstream" else outgoing(b, current)
        for link in links:
            neighbor = link.get("source") if direction == "upstream" else link.get("target")
            if neighbor in seen:
                continue
            seen.add(neighbor)
            artifact = by_id.get(neighbor, {"id": neighbor, "title": "Unknown artifact"})
            rows.append({"depth": depth + 1, "id": neighbor, "title": artifact.get("title", ""), "type": artifact.get("type", ""), "stage": artifact.get("stage", ""), "tool": artifact.get("tool", ""), "link": link.get("type", "")})
            frontier.append((neighbor, depth + 1))
    return rows


def audit_bus(bus: dict[str, Any]) -> dict[str, Any]:
    b = ensure_bus(bus)
    ids = [a.get("id") for a in b["artifacts"]]
    duplicates = sorted({x for x in ids if ids.count(x) > 1 and x})
    known = set(ids)
    broken = [x for x in b["links"] if x.get("source") not in known or x.get("target") not in known]
    isolated = [a for a in b["artifacts"] if not any(x.get("source") == a.get("id") or x.get("target") == a.get("id") for x in b["links"])]
    return {"artifacts": len(b["artifacts"]), "links": len(b["links"]), "duplicate_ids": duplicates, "broken_links": broken, "isolated_artifacts": [a.get("id") for a in isolated]}
