"""Literature retrieval and evidence-preparation utilities.

Uses public scholarly metadata APIs. Metadata is not treated as evidence for claims.
"""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
from typing import Any


def _get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "SciMantra/LiteratureRetriever/0.1 (mailto:research@scimantra.com)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _year(item: dict[str, Any]) -> str:
    parts = item.get("published", {}).get("date-parts", [[""]])
    return str(parts[0][0]) if parts and parts[0] and parts[0][0] else ""


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def relevance_score(query: str, title: str) -> float:
    q = set(_normalize_title(query).split())
    t = set(_normalize_title(title).split())
    if not q or not t:
        return 0.0
    return round(100 * len(q & t) / len(q), 1)


def crossref_retrieve(query: str, rows: int = 25) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"query.bibliographic": query, "rows": rows, "select": "DOI,title,author,published,container-title,type,URL"})
    data = _get_json("https://api.crossref.org/works?" + params)
    out = []
    for item in data.get("message", {}).get("items", []):
        title = (item.get("title") or [""])[0]
        authors = item.get("author") or []
        author = ", ".join((a.get("family") or a.get("name") or "") for a in authors[:5]).strip(", ")
        out.append({"Title": title, "Year": _year(item), "Authors": author, "Journal": (item.get("container-title") or [""])[0], "DOI": item.get("DOI", ""), "Type": item.get("type", ""), "URL": item.get("URL", ""), "Relevance": relevance_score(query, title), "Source": "Crossref"})
    return out


def deduplicate(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result = []
    for paper in sorted(papers, key=lambda p: (-float(p.get("Relevance", 0)), str(p.get("Year", ""))),):
        key = (str(paper.get("DOI", "")).lower().strip() or _normalize_title(str(paper.get("Title", ""))))
        if key and key not in seen:
            seen.add(key)
            result.append(paper)
    return result


def retrieve_and_rank(query: str, rows: int = 25) -> list[dict[str, Any]]:
    return deduplicate(crossref_retrieve(query, rows))


def evidence_ready_record(paper: dict[str, Any]) -> dict[str, Any]:
    """Create a safe matrix seed; no claims are inferred from metadata."""
    return {"Title": paper.get("Title", ""), "Year": paper.get("Year", ""), "Authors": paper.get("Authors", ""), "Journal": paper.get("Journal", ""), "DOI": paper.get("DOI", ""), "Source": paper.get("Source", ""), "Problem": "", "Challenges": "", "Research solution": "", "Technology / approach": "", "Innovation": "", "Difference from previous work": "", "Research gap": "", "Method": "", "Key result": "", "Limitation": "", "Evidence location": "", "Evidence status": "Metadata only — full text verification required"}
