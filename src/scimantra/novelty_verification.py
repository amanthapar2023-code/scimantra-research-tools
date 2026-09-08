"""Structured prior-art challenge for research novelty claims.

This module does not perform live literature retrieval. It compares researcher-supplied
prior work against a proposed contribution and highlights dimensions requiring verification.
"""
from __future__ import annotations
from typing import Any

DIMENSIONS = [
    ("Problem", "Is the same scientific or engineering problem already addressed?"),
    ("Method", "Is the core method or algorithm materially the same?"),
    ("System / model", "Is the same organism, material, dataset, platform, or model used?"),
    ("Intervention", "Is the same intervention, treatment, exposure, or manipulation used?"),
    ("Outcome", "Is the same primary endpoint or outcome measured?"),
    ("Mechanism", "Is the same mechanistic explanation or pathway proposed?"),
    ("Application", "Is the same practical application or use case demonstrated?"),
    ("Combination", "Is the claimed novelty merely a combination of already-known elements?"),
    ("Scope", "Does the proposed work add a meaningful boundary, population, condition, or capability?"),
    ("Evidence", "Does the prior work already contain evidence substantially supporting the proposed contribution?"),
]
STATUSES = ["Not assessed", "Distinct", "Similar", "Highly similar", "Same / already demonstrated", "Unclear"]

def template_rows():
    return [{"Dimension": d, "Question": q, "Status": "Not assessed", "Prior work evidence": "", "Proposed contribution": "", "Verification note": ""} for d, q in DIMENSIONS]

def audit(rows):
    weights = {"Distinct": 1.0, "Similar": .6, "Highly similar": .3, "Same / already demonstrated": 0.0, "Unclear": .4, "Not assessed": None}
    assessed = [r for r in rows if r.get("Status") != "Not assessed"]
    score = round(100 * sum(weights.get(r.get("Status"), .4) for r in assessed) / len(assessed), 1) if assessed else 0.0
    return {"dimensions": len(rows), "assessed": len(assessed), "score": score, **{s: sum(r.get("Status") == s for r in rows) for s in STATUSES}}

def priority_queue(rows):
    p = {"Same / already demonstrated": 100, "Highly similar": 85, "Similar": 60, "Unclear": 50, "Not assessed": 35, "Distinct": 0}
    return sorted([{"Priority": p.get(r.get("Status"), 35), "Dimension": r.get("Dimension", ""), "Status": r.get("Status", "Not assessed"), "Action": "Reframe or identify a genuinely differentiating contribution" if r.get("Status") in {"Same / already demonstrated", "Highly similar"} else "Verify against the cited prior work" if r.get("Status") in {"Similar", "Unclear", "Not assessed"} else "Document the distinction"} for r in rows], key=lambda x: x["Priority"], reverse=True)

def export_audit(rows, summary):
    lines = ["# SciMantra Novelty Verification & Prior-Art Challenge", "", f"Planning distinctiveness score: {summary['score']}/100", "", "> This is not a patentability opinion or proof of novelty. It is a structured challenge using researcher-supplied prior work and requires verification against the literature and relevant databases.", ""]
    for r in rows:
        lines += [f"## {r['Dimension']} — {r['Status']}", f"- Question: {r['Question']}", f"- Prior work evidence: {r.get('Prior work evidence','')}", f"- Proposed contribution: {r.get('Proposed contribution','')}", f"- Verification note: {r.get('Verification note','')}", ""]
    return "\n".join(lines)
