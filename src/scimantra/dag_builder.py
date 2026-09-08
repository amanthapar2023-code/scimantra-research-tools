"""Directed acyclic graph planning helpers for causal research design."""

from __future__ import annotations

from typing import Dict, List, Tuple

NODE_ROLES = ["Exposure", "Outcome", "Confounder", "Mediator", "Collider", "Covariate", "Negative control", "Unclassified"]
EDGE_TYPES = ["causes / influences", "associated with", "measured before", "measured after", "unknown"]


def node(name: str, role: str = "Unclassified", rationale: str = "") -> Dict[str, str]:
    return {"Variable": name.strip(), "Role": role, "Rationale": rationale.strip()}


def edge(source: str, target: str, relation: str = "causes / influences", rationale: str = "") -> Dict[str, str]:
    return {"From": source.strip(), "To": target.strip(), "Relationship": relation, "Rationale": rationale.strip()}


def build_starter_dag(exposure: str, outcome: str, confounders: List[str] | None = None) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Create a transparent starter structure; all inferred links are marked as planning hypotheses."""
    exposure = exposure.strip() or "Exposure / intervention"
    outcome = outcome.strip() or "Outcome"
    nodes = [node(exposure, "Exposure", "Researcher-provided exposure/intervention."), node(outcome, "Outcome", "Researcher-provided outcome.")]
    edges = [edge(exposure, outcome, "causes / influences", "Candidate causal pathway; verify with study design.")]
    for item in confounders or []:
        if item.strip():
            nodes.append(node(item, "Confounder", "Candidate confounder domain; researcher must verify causal role."))
            edges.extend([
                edge(item, exposure, "causes / influences", "Candidate pathway; verify."),
                edge(item, outcome, "causes / influences", "Candidate pathway; verify."),
            ])
    return nodes, edges


def audit_dag(nodes: List[Dict[str, str]], edges: List[Dict[str, str]]) -> Dict[str, object]:
    names = {n.get("Variable", "").strip() for n in nodes if n.get("Variable", "").strip()}
    dangling = [e for e in edges if e.get("From", "").strip() not in names or e.get("To", "").strip() not in names]
    duplicate_nodes = sorted({x for x in names if sum(n.get("Variable", "").strip() == x for n in nodes) > 1})
    role_counts = {role: sum(n.get("Role") == role for n in nodes) for role in NODE_ROLES}
    incoming = {x: 0 for x in names}
    outgoing = {x: 0 for x in names}
    for e in edges:
        s, t = e.get("From", "").strip(), e.get("To", "").strip()
        if s in outgoing and t in incoming:
            outgoing[s] += 1
            incoming[t] += 1
    isolated = sorted(x for x in names if incoming[x] == 0 and outgoing[x] == 0)
    exposure = [n["Variable"] for n in nodes if n.get("Role") == "Exposure"]
    outcome = [n["Variable"] for n in nodes if n.get("Role") == "Outcome"]
    mediator_adjustment_warning = [n["Variable"] for n in nodes if n.get("Role") == "Mediator"]
    collider_warning = [n["Variable"] for n in nodes if n.get("Role") == "Collider"]
    return {
        "nodes": len(nodes), "edges": len(edges), "dangling_edges": len(dangling),
        "duplicate_nodes": duplicate_nodes, "isolated_nodes": isolated,
        "role_counts": role_counts, "exposures": exposure, "outcomes": outcome,
        "mediator_adjustment_warning": mediator_adjustment_warning,
        "collider_warning": collider_warning,
        "structural_status": "Review required" if dangling or duplicate_nodes else "Structurally coherent",
    }


def adjustment_guidance(nodes: List[Dict[str, str]]) -> List[Dict[str, str]]:
    rows = []
    for n in nodes:
        role = n.get("Role", "Unclassified")
        if role == "Confounder":
            action, reason = "Consider adjustment", "Candidate common cause; verify temporality and causal structure before adjustment."
        elif role == "Mediator":
            action, reason = "Do not automatically adjust", "Adjusting can remove part of a causal pathway; estimand must be defined first."
        elif role == "Collider":
            action, reason = "Avoid conditioning unless justified", "Conditioning on a collider can create a non-causal association."
        elif role == "Exposure":
            action, reason = "Primary exposure", "Define intervention/exposure and its measurement."
        elif role == "Outcome":
            action, reason = "Primary outcome", "Define outcome timing and measurement."
        else:
            action, reason = "Researcher review", "Causal role is not established by the label alone."
        rows.append({"Variable": n.get("Variable", ""), "Role": role, "Suggested action": action, "Why": reason})
    return rows


def export_dag(nodes: List[Dict[str, str]], edges: List[Dict[str, str]], audit: Dict[str, object]) -> str:
    lines = ["# DAG & Causal Structure Builder", "", "> Planning artifact only. Arrows and variable roles are hypotheses to verify, not causal facts.", "", "## Nodes"]
    for n in nodes:
        lines.append(f"- {n.get('Variable')} — {n.get('Role')}: {n.get('Rationale')}")
    lines += ["", "## Edges"]
    for e in edges:
        lines.append(f"- {e.get('From')} → {e.get('To')} — {e.get('Relationship')}: {e.get('Rationale')}")
    lines += ["", "## Audit", f"- Structural status: {audit.get('structural_status')}", f"- Nodes: {audit.get('nodes')}", f"- Edges: {audit.get('edges')}", f"- Dangling edges: {audit.get('dangling_edges')}"]
    return "\n".join(lines)
