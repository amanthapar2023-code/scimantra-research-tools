"""Phase 107: durable-in-shape research decision and learning memory.

Records researcher decisions, rationale, outcomes, failed approaches and lessons
so they can be reused across the Research OS. This is a provenance/coordination
layer; it does not decide scientific truth.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import json
from typing import Any

KINDS = ["Decision", "Failed approach", "Lesson", "Assumption", "Open question", "Milestone"]
OUTCOMES = ["Not assessed", "Successful", "Partially successful", "Failed", "Superseded", "Needs follow-up"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_memory(project_id: str = "") -> dict[str, Any]:
    return {"schema_version": 1, "project_id": project_id.strip(), "records": [], "updated_at": _now()}


def record(memory: dict[str, Any], record_id: str, kind: str, title: str, rationale: str = "", outcome: str = "Not assessed", evidence_ids: list[str] | None = None, stage: str = "", tags: list[str] | None = None) -> dict[str, Any]:
    if kind not in KINDS: raise ValueError(f"Unsupported memory kind: {kind}")
    if outcome not in OUTCOMES: raise ValueError(f"Unsupported outcome: {outcome}")
    if not record_id.strip() or not title.strip(): raise ValueError("record_id and title are required")
    out = deepcopy(memory)
    rows = out.setdefault("records", [])
    if any(x.get("id") == record_id.strip() for x in rows): raise ValueError(f"Memory ID already exists: {record_id}")
    rows.append({"id": record_id.strip(), "kind": kind, "title": title.strip(), "rationale": rationale.strip(), "outcome": outcome, "evidence_ids": [x.strip() for x in (evidence_ids or []) if x.strip()], "stage": stage.strip(), "tags": [x.strip() for x in (tags or []) if x.strip()], "created_at": _now()})
    out["updated_at"] = _now()
    return out


def search(memory: dict[str, Any], query: str = "", kind: str = "") -> list[dict[str, Any]]:
    q = query.strip().lower()
    return [r for r in memory.get("records", []) if (not kind or r.get("kind") == kind) and (not q or q in json.dumps(r, ensure_ascii=False).lower())]


def audit(memory: dict[str, Any], bus: dict[str, Any] | None = None) -> dict[str, Any]:
    rows = memory.get("records", [])
    ids = [r.get("id") for r in rows]
    dup = sorted({x for x in ids if x and ids.count(x) > 1})
    known = {a.get("id") for a in (bus or {}).get("artifacts", [])}
    broken = [{"id": r.get("id"), "missing_evidence": [x for x in r.get("evidence_ids", []) if x not in known]} for r in rows if bus and any(x not in known for x in r.get("evidence_ids", []))]
    follow = [r for r in rows if r.get("outcome") in {"Failed", "Partially successful", "Needs follow-up", "Superseded"}]
    return {"records": len(rows), "duplicates": dup, "broken_evidence": broken, "follow_up": len(follow), "healthy": not dup and not broken}


def reusable_lessons(memory: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in memory.get("records", []) if r.get("kind") in {"Lesson", "Failed approach"} and r.get("outcome") in {"Successful", "Failed", "Partially successful"}]


def summary(memory: dict[str, Any]) -> dict[str, Any]:
    rows = memory.get("records", [])
    return {"records": len(rows), "decisions": sum(r.get("kind") == "Decision" for r in rows), "failed_approaches": sum(r.get("kind") == "Failed approach" for r in rows), "lessons": sum(r.get("kind") == "Lesson" for r in rows), "follow_up": sum(r.get("outcome") in {"Failed", "Partially successful", "Needs follow-up", "Superseded"} for r in rows)}


def export_json(memory: dict[str, Any]) -> str:
    return json.dumps(memory, indent=2, ensure_ascii=False)
