"""Structured literature-evidence workspace for SciMantra.

The extractor intentionally labels fields as unverified unless supplied by the
researcher or extracted from an actual paper. It never invents findings.
"""
from __future__ import annotations

FIELDS = [
    "Problem", "Challenges", "Research solution", "Technology / approach",
    "Innovation", "Difference from previous work", "Research gap",
    "Method", "Key result", "Limitation", "Evidence location", "Confidence"
]


def empty_record(title: str = "") -> dict[str, str]:
    return {"Paper": title, **{field: "" for field in FIELDS}}


def evidence_status(record: dict[str, str]) -> str:
    filled = sum(bool(str(record.get(k, "")).strip()) for k in FIELDS if k not in {"Confidence"})
    if filled == 0:
        return "NOT EXTRACTED"
    if record.get("Evidence location", "").strip():
        return "SOURCE-ANCHORED"
    return "PARTIAL — LOCATION NEEDED"


def matrix_score(records: list[dict[str, str]]) -> dict[str, float]:
    if not records:
        return {"coverage": 0.0, "source_anchored": 0.0}
    possible = len(records) * (len(FIELDS) - 1)
    filled = sum(bool(str(r.get(k, "")).strip()) for r in records for k in FIELDS if k != "Confidence")
    anchored = sum(bool(str(r.get("Evidence location", "")).strip()) for r in records)
    return {"coverage": round(100 * filled / possible, 1), "source_anchored": round(100 * anchored / len(records), 1)}


def gap_candidates(records: list[dict[str, str]]) -> list[str]:
    gaps = []
    for field, label in [("Limitation", "limitations"), ("Research gap", "explicit gaps"), ("Difference from previous work", "comparative detail"), ("Evidence location", "source locations")]:
        missing = sum(not str(r.get(field, "")).strip() for r in records)
        if missing:
            gaps.append(f"{missing}/{len(records)} papers lack {label}; do not infer the missing information until the source is checked.")
    return gaps
