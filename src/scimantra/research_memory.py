"""Structured project memory for research decisions and provenance."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

CATEGORIES = ["Literature", "Decision", "Experiment", "Dataset", "Claim", "Evidence", "Failure", "Insight", "Task"]

def memory_item(category: str, title: str, content: str, source: str = "", status: str = "Active") -> dict[str, Any]:
    return {"Category": category, "Title": title, "Content": content, "Source": source, "Status": status, "Timestamp": datetime.now(timezone.utc).isoformat()}

def add_memory(memory: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    return memory + [item]

def search_memory(memory: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return memory
    return [m for m in memory if q in " ".join(str(m.get(k, "")) for k in ("Category", "Title", "Content", "Source")).lower()]

def memory_stats(memory: list[dict[str, Any]]) -> dict[str, int]:
    return {category: sum(1 for m in memory if m.get("Category") == category) for category in CATEGORIES}

def export_memory(memory: list[dict[str, Any]]) -> str:
    lines = ["# SciMantra Research Memory", "", "Structured project memory. Entries preserve researcher-provided information and provenance; they are not independently verified.", ""]
    for m in memory:
        lines += [f"## {m.get('Category','Other')}: {m.get('Title','Untitled')}", f"- Status: {m.get('Status','')}", f"- Source: {m.get('Source','')}", f"- Recorded: {m.get('Timestamp','')}", "", m.get('Content',''), ""]
    return "\n".join(lines)
