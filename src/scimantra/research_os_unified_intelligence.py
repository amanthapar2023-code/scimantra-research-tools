"""Phase 109: unified Research OS intelligence snapshot.

Combines contextual state, workflow audit, next actions, artifact/bus health and
research memory into one transparent decision-support report.
"""
from __future__ import annotations
from typing import Any
from .research_os_context import build_context
from .research_os_data_bus import audit_bus
from .research_os_decision_memory import audit as audit_memory
from .research_os_next_action import recommend
from .research_os_workflow_runner import audit_run

LEVELS = ["Critical", "High", "Medium", "Low"]

def analyze(project=None, bus=None, run=None, memory=None, audit_signals=None):
    project = project or {}; bus = bus or {}; run = run or {}; memory = memory or {"records": []}
    context = build_context(project, bus, run, memory, audit_signals or [])
    workflow = audit_run(run, bus) if run.get("steps") else {"steps":0,"complete":0,"ready":[],"blocked":[],"issues":[],"completion_pct":0.0}
    bus_report = audit_bus(bus)
    memory_report = audit_memory(memory, bus)
    actions = recommend(run, bus, audit_signals or [])
    health = 100
    health -= min(30, len(workflow.get("issues", []))*10)
    health -= min(25, len(bus_report.get("broken_links", []))*10)
    health -= min(20, len(memory_report.get("broken_evidence", []))*5)
    health -= min(25, len(workflow.get("blocked", []))*10)
    return {"health_score": max(0, health), "context": context, "workflow": workflow, "bus": bus_report, "memory": memory_report, "top_actions": actions[:5], "decision_state": _state(workflow, bus_report, memory_report, actions)}

def _state(workflow, bus, memory, actions):
    if workflow.get("blocked"): return "Blocked — resolve workflow blockers"
    if bus.get("broken_links") or memory.get("broken_evidence"): return "Needs repair — resolve structural links"
    if actions: return "Active — next research actions identified"
    if workflow.get("steps") and workflow.get("complete") == workflow.get("steps"): return "Complete — prepare next research cycle"
    return "Setup — establish project context and artifacts"

def summary(report):
    return {"health_score": report.get("health_score",0), "decision_state": report.get("decision_state",""), "actions": len(report.get("top_actions",[])), "workflow_completion": report.get("workflow",{}).get("completion_pct",0), "bus_healthy": not bool(report.get("bus",{}).get("broken_links")), "memory_healthy": not bool(report.get("memory",{}).get("broken_evidence"))}
