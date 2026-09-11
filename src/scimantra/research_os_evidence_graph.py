"""Phase 110: evidence graph integration for the Research OS.

Builds an explicit provenance chain from source/evidence through analysis,
results and claims. It reports graph structure only; it never decides whether
a scientific claim is true.
"""
from __future__ import annotations
from collections import defaultdict, deque
from typing import Any

NODE_TYPES = ["Literature source", "Raw evidence", "Dataset", "Analysis", "Result", "Figure", "Table", "Claim", "Manuscript"]
EDGE_TYPES = ["derived_from", "supports", "tests", "cites", "contradicts", "revises"]


def build_graph(bus: dict[str, Any] | None = None) -> dict[str, Any]:
    bus = bus or {}
    nodes = []
    for a in bus.get("artifacts", []):
        typ = a.get("type", "Other")
        if typ in NODE_TYPES or a.get("id"):
            nodes.append({"id": a.get("id", ""), "label": a.get("title", ""), "type": typ, "stage": a.get("stage", ""), "tool": a.get("source_tool", a.get("tool", ""))})
    edges = [{"source": x.get("source"), "target": x.get("target"), "type": x.get("type", "supports"), "note": x.get("note", "")} for x in bus.get("links", [])]
    return {"nodes": nodes, "edges": edges}


def audit_graph(graph: dict[str, Any]) -> dict[str, Any]:
    ids = {n.get("id") for n in graph.get("nodes", [])}
    broken = [e for e in graph.get("edges", []) if e.get("source") not in ids or e.get("target") not in ids]
    incoming = defaultdict(int)
    outgoing = defaultdict(int)
    for e in graph.get("edges", []): incoming[e.get("target")] += 1; outgoing[e.get("source")] += 1
    claims = [n for n in graph.get("nodes", []) if n.get("type") == "Claim"]
    unsupported_claims = [n.get("id") for n in claims if incoming[n.get("id")] == 0]
    isolated = [n.get("id") for n in graph.get("nodes", []) if incoming[n.get("id")] == 0 and outgoing[n.get("id")] == 0]
    return {"nodes": len(graph.get("nodes", [])), "edges": len(graph.get("edges", [])), "broken_edges": broken, "unsupported_claims": unsupported_claims, "isolated_nodes": isolated, "healthy": not broken}


def trace(graph: dict[str, Any], node_id: str, direction: str = "upstream", max_depth: int = 8) -> list[dict[str, Any]]:
    if direction not in {"upstream", "downstream"}: raise ValueError("direction must be upstream or downstream")
    by_id = {n.get("id"): n for n in graph.get("nodes", [])}; seen={node_id}; q=deque([(node_id,0)]); rows=[]
    while q:
        current, depth=q.popleft()
        if depth >= max_depth: continue
        for e in graph.get("edges", []):
            neighbor = e.get("source") if direction == "upstream" and e.get("target") == current else e.get("target") if direction == "downstream" and e.get("source") == current else None
            if neighbor and neighbor not in seen:
                seen.add(neighbor); n=by_id.get(neighbor,{"id":neighbor}); rows.append({"depth":depth+1,"id":neighbor,"label":n.get("label",""),"type":n.get("type",""),"stage":n.get("stage",""),"edge":e.get("type","")}); q.append((neighbor,depth+1))
    return rows


def claim_coverage(graph: dict[str, Any]) -> list[dict[str, Any]]:
    incoming = defaultdict(list)
    for e in graph.get("edges", []): incoming[e.get("target")].append(e)
    return [{"claim_id": n.get("id"), "claim": n.get("label"), "linked_sources": len(incoming[n.get("id")]), "supported_structurally": bool(incoming[n.get("id")])} for n in graph.get("nodes", []) if n.get("type") == "Claim"]


def summary(graph: dict[str, Any]) -> dict[str, Any]:
    a=audit_graph(graph); return {"nodes":a["nodes"],"edges":a["edges"],"claims":sum(n.get("type")=="Claim" for n in graph.get("nodes", [])),"claims_without_incoming":len(a["unsupported_claims"]),"healthy":a["healthy"]}
