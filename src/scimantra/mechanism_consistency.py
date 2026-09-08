"""Mechanism / explanation consistency audit for research claims."""
from __future__ import annotations
from typing import Any

DOMAINS = [
    ("Mechanism directly measured", "Is the proposed mechanism itself measured rather than inferred only from an endpoint?"),
    ("Evidence chain", "Is there a traceable chain from intervention/exposure to intermediate process to outcome?"),
    ("Temporal ordering", "Does the proposed mechanism occur before the claimed outcome?"),
    ("Alternative explanations", "Have plausible non-mechanistic explanations been considered or challenged?"),
    ("Manipulation / perturbation", "Was the mechanism perturbed, blocked, rescued, or otherwise tested where appropriate?"),
    ("Measurement specificity", "Could the measured signal have multiple biological or technical interpretations?"),
    ("Causal scope", "Does the design justify mechanistic or causal wording, rather than association alone?"),
    ("Literature alignment", "Is the proposed explanation consistent with relevant established evidence?"),
    ("Contradictory evidence", "Are observations that weaken the proposed mechanism acknowledged?"),
    ("Conclusion wording", "Is the final mechanistic wording no stronger than the evidence supports?"),
]
LEVELS = ["Not assessed", "Consistent", "Partially consistent", "Weak / indirect", "Contradictory"]

def template_rows():
    return [{"Domain": d, "Question": q, "Assessment": "Not assessed", "Evidence": "", "Alternative explanation": "", "Notes": ""} for d, q in DOMAINS]

def audit(rows):
    weights = {"Consistent": 1.0, "Partially consistent": .6, "Weak / indirect": .25, "Contradictory": 0.0, "Not assessed": None}
    assessed = [r for r in rows if r.get("Assessment") != "Not assessed"]
    score = round(100 * sum(weights.get(r.get("Assessment"), 0) for r in assessed) / len(assessed), 1) if assessed else 0.0
    return {"domains": len(rows), "assessed": len(assessed), "score": score, **{x: sum(r.get("Assessment") == x for r in rows) for x in LEVELS}}

def priority_queue(rows):
    priority = {"Contradictory": 100, "Weak / indirect": 80, "Not assessed": 50, "Partially consistent": 35, "Consistent": 0}
    return sorted([{"Priority": priority.get(r.get("Assessment"), 50), "Domain": r.get("Domain", ""), "Assessment": r.get("Assessment", "Not assessed"), "Action": "Test or qualify the mechanism" if r.get("Assessment") in {"Contradictory", "Weak / indirect"} else "Add evidence or explicit limitation" if r.get("Assessment") == "Not assessed" else "Document supporting evidence"} for r in rows], key=lambda x: x["Priority"], reverse=True)

def export_audit(rows, summary):
    lines = ["# SciMantra Mechanism / Explanation Consistency Audit", "", f"Planning score: {summary['score']}/100", "", "> This audit does not establish a biological mechanism or causal truth. It organizes researcher-supplied evidence, alternatives, and wording boundaries.", ""]
    for r in rows:
        lines += [f"## {r['Domain']} — {r['Assessment']}", f"- Question: {r['Question']}", f"- Evidence: {r.get('Evidence','')}", f"- Alternative explanation: {r.get('Alternative explanation','')}", f"- Notes: {r.get('Notes','')}", ""]
    return "\n".join(lines)
