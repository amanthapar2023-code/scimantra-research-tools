"""Novelty and research-gap validation helpers.

This module produces candidate warnings from researcher-supplied evidence and
bibliographic metadata. It never declares scientific novelty as a fact.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any


def _tokens(text: str) -> set[str]:
    stop = {"the","and","for","with","using","use","of","in","on","to","a","an","from","by","via","based","study","studies","analysis","effect","effects","novel","approach","method","methods","investigation","development"}
    return {x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text or "") if x.lower() not in stop}


def concept_similarity(a: str, b: str) -> float:
    x, y = _tokens(a), _tokens(b)
    return round(len(x & y) / max(1, len(x | y)), 3)


def _filled(records: list[dict[str, str]], field: str) -> list[str]:
    return [str(r.get(field, "")).strip() for r in records if str(r.get(field, "")).strip()]


def detect_patterns(records: list[dict[str, str]]) -> dict[str, Any]:
    patterns: list[dict[str, Any]] = []
    for field, label in [("Technology / approach", "Repeated technology/approach"), ("Method", "Repeated method pattern"), ("Limitation", "Repeated limitation pattern"), ("Research gap", "Repeatedly reported gap")]:
        values = _filled(records, field)
        if len(values) >= 2:
            words = Counter(w for value in values for w in _tokens(value))
            common = [w for w, n in words.most_common(8) if n >= 2]
            if common:
                patterns.append({"type": label, "signal": ", ".join(common), "count": len(values), "verification": f"Check the cited {field.lower()} entries in the source papers before treating this as a field-wide pattern."})
    missing_controls = sum(not str(r.get("Difference from previous work", "")).strip() for r in records)
    missing_locations = sum(not str(r.get("Evidence location", "")).strip() for r in records)
    if missing_controls:
        patterns.append({"type":"Comparator evidence gap","signal":f"{missing_controls}/{len(records)} papers lack comparative detail","count":missing_controls,"verification":"Inspect each paper for its control, benchmark, comparator, or baseline."})
    if missing_locations:
        patterns.append({"type":"Provenance gap","signal":f"{missing_locations}/{len(records)} papers lack evidence locations","count":missing_locations,"verification":"Record page/section/table/figure/DOI locations before using the claim in a manuscript."})
    return {"patterns": patterns}


def validate_direction(title: str, proposed_direction: str, papers: list[dict[str, Any]], records: list[dict[str, str]]) -> dict[str, Any]:
    collisions = []
    for p in papers:
        score = concept_similarity(proposed_direction or title, p.get("Title", ""))
        if score >= 0.35:
            collisions.append({"score": score, "title": p.get("Title", "Untitled"), "doi": p.get("DOI", ""), "warning": "Conceptually related title; full-text comparison required."})
    collisions.sort(key=lambda x: x["score"], reverse=True)
    patterns = detect_patterns(records)["patterns"]
    warnings = []
    if collisions:
        warnings.append("The proposed direction overlaps with retrieved literature at the concept level. Do not claim novelty until the closest papers are compared at full-text/claim level.")
    if any(p["type"] == "Repeated limitation pattern" for p in patterns):
        warnings.append("Repeated limitations may define a defensible gap, but only if the limitations are genuinely documented and your study addresses them.")
    if any(p["type"] == "Repeated technology/approach" for p in patterns):
        warnings.append("A commonly used technology is not itself novelty. Novelty may require a new question, combination, mechanism, validation setting, or evidence—verify against literature.")
    confidence = "LOW" if not papers else ("REVIEW REQUIRED" if collisions else "NO CLOSE TITLE COLLISION FOUND")
    return {"status": confidence, "collisions": collisions[:10], "patterns": patterns, "warnings": warnings}
