"""Phase 108: unified contextual layer for SciMantra Research OS.

Combines project, workflow, artifacts, next actions and research memory into a
single explicit context snapshot. It summarizes state; it does not infer
scientific truth.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from .research_os_data_bus import ensure_bus, summary as bus_summary
from .research_os_next_action import recommend
from .research_os_decision_memory import summary as memory_summary


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_context(project: dict[str, Any] | None = None, bus: dict[str, Any] | None = None, run: dict[str, Any] | None = None, memory: dict[str, Any] | None = None, audit_signals: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    project = project or {}
    bus = ensure_bus(bus)
    memory = memory or {"records": []}
    recs = recommend(run or {}, bus, audit_signals or [])
    return {
        "schema_version": 1,
        "generated_at": _now(),
        "project": project.get("project", project),
        "workflow": {"id": (run or {}).get("workflow_id", ""), "run_id": (run or {}).get("run_id", ""), "steps": (run or {}).get("steps", [])},
        "bus": bus_summary(bus),
        "memory": memory_summary(memory),
        "next_actions": recs[:10],
        "context_flags": _flags(project, bus, run or {}, memory),
    }


def _flags(project: dict[str, Any], bus: dict[str, Any], run: dict[str, Any], memory: dict[str, Any]) -> list[str]:
    flags = []
    if not (project.get("project", project).get("question", "") if isinstance(project.get("project", project), dict) else ""): flags.append("Central research question is not recorded")
    if not bus.get("artifacts"): flags.append("No shared Research OS artifacts registered")
    if run and any(s.get("status") == "Blocked" for s in run.get("steps", [])): flags.append("Workflow contains blocked steps")
    if not memory.get("records"): flags.append("No decision/learning memory recorded")
    if bus_summary(bus).get("healthy") is False: flags.append("Shared data bus has structural audit issues")
    return flags


def stage_snapshot(project: dict[str, Any]) -> list[dict[str, Any]]:
    stages = project.get("stages", []) if isinstance(project, dict) else []
    if isinstance(stages, dict):
        return [{"stage": k, **(v if isinstance(v, dict) else {"status": str(v)})} for k, v in stages.items()]
    return stages if isinstance(stages, list) else []


def context_summary(context: dict[str, Any]) -> dict[str, Any]:
    return {"project": context.get("project", {}).get("name", "") if isinstance(context.get("project"), dict) else "", "workflow": context.get("workflow", {}).get("id", ""), "artifacts": context.get("bus", {}).get("artifacts", 0), "memory_records": context.get("memory", {}).get("records", 0), "next_actions": len(context.get("next_actions", [])), "flags": len(context.get("context_flags", []))}
