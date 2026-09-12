"""Phase 113: adapter layer for legacy SciMantra tool outputs.

Converts existing output metadata into the canonical Research OS contract without
altering scientific payloads. Readiness here means structural compatibility only.
"""
from __future__ import annotations
from typing import Any
from .research_os_data_contract import envelope, validate
from .research_os_tool_adapters import TOOL_REGISTRY

READINESS = ("Ready", "Needs adapter", "Unknown")

def inspect_tool(source_tool: str) -> dict[str, Any]:
    if source_tool not in TOOL_REGISTRY:
        return {"tool": source_tool, "status": "Unknown", "reason": "Tool is not registered in the Research OS adapter registry."}
    module, stage = TOOL_REGISTRY[source_tool]
    return {"tool": source_tool, "module": module, "stage": stage, "status": "Ready", "reason": "Registered adapter contract available."}

def adapt_output(source_tool: str, project_id: str, artifact_id: str, title: str, artifact_type: str = "Other", stage: str = "", status: str = "Draft", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    info = inspect_tool(source_tool)
    if info["status"] == "Unknown": raise ValueError(info["reason"])
    record = envelope(project_id, artifact_id, artifact_type, stage or info["stage"], source_tool, status, payload)
    errors = validate(record)
    return {"record": record, "valid": not errors, "errors": errors, "adapter": info}

def audit_registry() -> dict[str, Any]:
    rows = [inspect_tool(name) for name in TOOL_REGISTRY]
    ready = sum(r["status"] == "Ready" for r in rows)
    return {"total": len(rows), "ready": ready, "needs_adapter": sum(r["status"] == "Needs adapter" for r in rows), "unknown": sum(r["status"] == "Unknown" for r in rows), "coverage_pct": round(100 * ready / len(rows), 1) if rows else 0.0, "rows": rows}

def adapter_report() -> str:
    import json
    return json.dumps({"phase": 113, "purpose": "Structural integration readiness", "audit": audit_registry()}, indent=2, ensure_ascii=False)
