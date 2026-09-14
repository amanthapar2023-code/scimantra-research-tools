"""Project-level research knowledge vault."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

OBJECT_TYPES = ["Research question", "Hypothesis", "Paper", "Evidence", "Experiment", "Dataset", "Analysis", "Result", "Claim", "Decision", "Limitation", "Idea"]
STATUSES = ["Planned", "In progress", "Verified", "Blocked", "Archived"]

def new_object(kind: str, title: str, content: str = "", source: str = "", status: str = "Planned", tags: str = "") -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {"id": now.strftime("%Y%m%d%H%M%S%f"), "type": kind, "title": title.strip(), "content": content.strip(), "source": source.strip(), "status": status, "tags": tags.strip(), "created_utc": now.isoformat()}

def vault_metrics(objects: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(objects)
    verified = sum(o.get("status") == "Verified" for o in objects)
    sourced = sum(bool(str(o.get("source", "")).strip()) for o in objects)
    return {"objects": total, "verified": verified, "sourced": sourced, "source_coverage": round(100*sourced/total, 1) if total else 0.0}

def search_objects(objects: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    terms = [x.lower() for x in query.split() if x.strip()]
    if not terms: return objects
    return [o for o in objects if all(t in " ".join(str(o.get(k, "")) for k in ("type", "title", "content", "source", "tags")).lower() for t in terms)]

def export_vault(objects: list[dict[str, Any]], project_title: str = "") -> str:
    lines = ["# SciMantra Research Knowledge Vault", "", f"Project: {project_title}", "", "Researcher-entered records with explicit provenance.", ""]
    for o in objects:
        lines += [f"## {o.get('type','Object')}: {o.get('title','')}", f"- Status: {o.get('status','')}", f"- Source: {o.get('source','') or '[MISSING]'}", f"- Tags: {o.get('tags','')}", "", o.get("content", "") or "[No content recorded]", ""]
    return "\n".join(lines)
