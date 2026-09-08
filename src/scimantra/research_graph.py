"""A lightweight research dependency graph: evidence objects and relationships."""
from __future__ import annotations
from typing import Any

NODE_TYPES = ["Question", "Hypothesis", "Experiment", "Variable", "Dataset", "Analysis", "Figure", "Result", "Claim", "Evidence", "Conclusion"]
EDGE_TYPES = ["tests", "measures", "uses", "produces", "visualizes", "supports", "contradicts", "depends_on", "answers"]

def node(node_id: str, node_type: str, label: str, source: str = "") -> dict[str, str]:
    return {"id": node_id, "type": node_type, "label": label.strip(), "source": source.strip()}

def edge(source: str, relation: str, target: str) -> dict[str, str]:
    return {"source": source, "relation": relation, "target": target}

def graph_audit(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    ids = {n.get("id") for n in nodes}
    dangling = [e for e in edges if e.get("source") not in ids or e.get("target") not in ids]
    connected = {x for e in edges for x in (e.get("source"), e.get("target"))}
    isolated = [n.get("id") for n in nodes if n.get("id") not in connected]
    return {"nodes": len(nodes), "edges": len(edges), "dangling_edges": len(dangling), "isolated_nodes": len(isolated), "connected_percent": round(100*(len(nodes)-len(isolated))/len(nodes), 1) if nodes else 0.0}

def export_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    lines = ["# Research Dependency Graph", "", "## Nodes"]
    for n in nodes: lines.append(f"- `{n['id']}` [{n['type']}]: {n['label']}")
    lines += ["", "## Relationships"]
    for e in edges: lines.append(f"- `{e['source']}` — **{e['relation']}** → `{e['target']}`")
    return "\n".join(lines)
