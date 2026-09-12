"""Phase 112: canonical Research OS exchange contract.

Defines the minimum envelope shared by project, artifact, provenance, workflow
and audit integrations. Structural validation only; no scientific inference.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 1
REQUIRED = ["schema_version", "project_id", "artifact_id", "artifact_type", "stage", "source_tool", "status", "created_at"]
STATUSES = ["Not assessed", "Draft", "Active", "Needs review", "Verified", "Archived", "Blocked", "Complete"]

def now() -> str: return datetime.now(timezone.utc).isoformat()

def envelope(project_id: str, artifact_id: str, artifact_type: str, stage: str, source_tool: str, status: str = "Draft", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if not project_id.strip() or not artifact_id.strip(): raise ValueError("project_id and artifact_id are required")
    if status not in STATUSES: raise ValueError(f"Unsupported status: {status}")
    return {"schema_version": SCHEMA_VERSION, "project_id": project_id.strip(), "artifact_id": artifact_id.strip(), "artifact_type": artifact_type.strip() or "Other", "stage": stage.strip(), "source_tool": source_tool.strip(), "status": status, "created_at": now(), "payload": payload or {}}

def validate(record: dict[str, Any]) -> list[str]:
    errors=[f"Missing required field: {x}" for x in REQUIRED if record.get(x) in (None, "")]
    if record.get("schema_version") != SCHEMA_VERSION: errors.append("Unsupported schema_version")
    if record.get("status") and record.get("status") not in STATUSES: errors.append("Unsupported status")
    return errors

def normalize(record: dict[str, Any]) -> dict[str, Any]:
    out=dict(record); out.setdefault("schema_version", SCHEMA_VERSION); out.setdefault("payload", {}); return out

def audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    ids=[r.get("artifact_id") for r in records]; dup=sorted({x for x in ids if x and ids.count(x)>1}); invalid=[]
    for r in records:
        e=validate(r)
        if e: invalid.append({"artifact_id":r.get("artifact_id",""),"errors":e})
    return {"records":len(records),"duplicates":dup,"invalid":invalid,"valid":not dup and not invalid}

def export_contract(records: list[dict[str, Any]]) -> str:
    import json
    return json.dumps({"schema_version":SCHEMA_VERSION,"records":records,"audit":audit(records)},indent=2,ensure_ascii=False)
