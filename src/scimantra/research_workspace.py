"""Project-level integration layer for the SciMantra research pipeline."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any

MODULES = [
    ("Research Intelligence", "ri_title", "ri_blueprint"),
    ("Evidence Matrix", "em_records", None),
    ("Methodology", "method_design", None),
    ("Results", "results_df", None),
    ("Claims", "claim_records", None),
    ("Reviewer Attack", "reviewer_rows", None),
    ("Reproducibility", "passport", None),
    ("Research Graph", "graph_nodes", "graph_edges"),
    ("Decision Engine", "decision_rows", None),
    ("Knowledge Vault", "research_vault", None),
]


def _count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, tuple, dict, set)):
        return len(value)
    try:
        return len(value)
    except Exception:
        return 1 if value else 0


def workspace_snapshot(session_state: Any) -> dict[str, Any]:
    """Normalize cross-page session state into a safe project snapshot."""
    get = session_state.get if hasattr(session_state, "get") else lambda k, d=None: d
    title = str(get("ri_title", "")).strip()
    blueprint = get("ri_blueprint")
    papers = get("ri_papers", []) or []
    records = get("em_records", []) or []
    design = get("method_design")
    claims = get("claim_records", []) or []
    reviewer = get("reviewer_rows", []) or []
    passport = get("passport")
    nodes = get("graph_nodes", []) or []
    edges = get("graph_edges", []) or []
    decisions = get("decision_rows", []) or []
    vault = get("research_vault", []) or []
    results_df = get("results_df")

    modules = {
        "Research Intelligence": {"present": bool(title or blueprint), "items": _count(papers), "detail": "Blueprint + literature metadata"},
        "Evidence Matrix": {"present": bool(records), "items": _count(records), "detail": "Literature evidence records"},
        "Methodology": {"present": bool(design), "items": _count(design), "detail": "Design specification"},
        "Results": {"present": results_df is not None, "items": _count(results_df), "detail": "Loaded analysis dataset"},
        "Claims": {"present": bool(claims), "items": _count(claims), "detail": "Claim-evidence records"},
        "Reviewer Attack": {"present": bool(reviewer), "items": _count(reviewer), "detail": "Reviewer challenges"},
        "Reproducibility": {"present": bool(passport), "items": _count(passport), "detail": "Passport fields"},
        "Research Graph": {"present": bool(nodes or edges), "items": _count(nodes), "relationships": _count(edges), "detail": "Dependency graph"},
        "Decision Engine": {"present": bool(decisions), "items": _count(decisions), "detail": "Ranked decisions"},
        "Knowledge Vault": {"present": bool(vault), "items": _count(vault), "detail": "Research objects"},
    }
    return {"project_title": title, "generated_utc": datetime.now(timezone.utc).isoformat(), "modules": modules}


def workspace_metrics(snapshot: dict[str, Any]) -> dict[str, Any]:
    modules = snapshot.get("modules", {})
    total = len(modules)
    active = sum(bool(v.get("present")) for v in modules.values())
    return {"modules": total, "active": active, "coverage": round(100 * active / total, 1) if total else 0.0}


def workspace_actions(snapshot: dict[str, Any]) -> list[str]:
    modules = snapshot.get("modules", {})
    order = list(modules)
    actions = []
    for i, name in enumerate(order[:-1]):
        if modules[name].get("present") and not modules[order[i + 1]].get("present"):
            actions.append(f"Connect {name} output to {order[i + 1]} input")
    if not modules.get("Research Intelligence", {}).get("present"):
        actions.append("Start with a research title in Research Intelligence")
    return actions


def export_workspace(snapshot: dict[str, Any], fmt: str = "markdown") -> str:
    if fmt == "json":
        return json.dumps(snapshot, indent=2, ensure_ascii=False, default=str)
    lines = ["# SciMantra Research Workspace", "", f"Project: {snapshot.get('project_title') or '[UNTITLED]'}", f"Generated: {snapshot.get('generated_utc', '')}", "", "Structural readiness snapshot — not a scientific validity certificate.", ""]
    for name, info in snapshot.get("modules", {}).items():
        state = "ACTIVE" if info.get("present") else "NOT CONNECTED"
        extra = f", relationships: {info.get('relationships') }" if "relationships" in info else ""
        lines.append(f"## {name} — {state}")
        lines.append(f"- Items: {info.get('items', 0)}{extra}")
        lines.append(f"- {info.get('detail', '')}")
        lines.append("")
    lines.append("## Next connections")
    for action in workspace_actions(snapshot) or ["No structural connection gaps detected"]:
        lines.append(f"- {action}")
    return "\n".join(lines)
