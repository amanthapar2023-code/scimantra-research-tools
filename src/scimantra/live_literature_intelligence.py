"""Live literature intelligence built on public scholarly metadata."""
from __future__ import annotations
from typing import Any
from .literature_retriever import retrieve_and_rank


def refresh(query: str, rows: int = 25, previous: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    papers = retrieve_and_rank(query, rows)
    old = {(str(p.get("DOI") or "").lower(), str(p.get("Title") or "").lower()) for p in (previous or [])}
    new = [p for p in papers if (str(p.get("DOI") or "").lower(), str(p.get("Title") or "").lower()) not in old]
    years = [int(p["Year"]) for p in papers if str(p.get("Year", "")).isdigit()]
    return {"query": query, "papers": papers, "new_papers": new, "count": len(papers), "new_count": len(new), "latest_year": max(years) if years else None, "source_note": "Scholarly metadata only; full-text verification is required before treating findings as evidence."}
