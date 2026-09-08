"""Deterministic adversarial reviewer checks for research planning."""
from __future__ import annotations
from typing import Any

CHECKS = [
    ("Primary question", "Is the primary research question explicit and answerable?", "major"),
    ("Comparator", "What is the comparator or reference condition, and why is it appropriate?", "major"),
    ("Controls", "Are essential positive, negative, vehicle, sham, or procedural controls present?", "major"),
    ("Experimental unit", "Is the true experimental/observational unit clearly defined?", "major"),
    ("Replication", "Are biological/independent replicates distinguished from technical repeats?", "major"),
    ("Randomization", "Could allocation or ordering introduce systematic bias?", "moderate"),
    ("Blinding", "Could measurement or analysis be influenced by knowledge of condition?", "moderate"),
    ("Confounding", "Which variables could explain the observed association besides the proposed factor?", "major"),
    ("Alternative explanation", "What competing mechanism could produce the same result?", "major"),
    ("Outcome definition", "Was the primary endpoint defined before inspecting results?", "major"),
    ("Analysis", "Is the planned analysis appropriate for the outcome, design, and data structure?", "major"),
    ("Missing data", "How will exclusions, missing observations, and failed measurements be handled?", "moderate"),
    ("Multiplicity", "Are multiple outcomes, groups, time points, or comparisons creating multiplicity risk?", "moderate"),
    ("Robustness", "Would the conclusion survive reasonable alternative specifications or sensitivity analyses?", "moderate"),
    ("Reproducibility", "Could an independent researcher reproduce the workflow from the recorded protocol and data?", "major"),
    ("Novelty", "Is the claimed contribution clearly differentiated from the closest prior work?", "major"),
]

def attack(title: str = "", method: str = "", result: str = "") -> list[dict[str, str]]:
    context = (title + " " + method + " " + result).lower()
    rows = []
    for area, question, severity in CHECKS:
        status = "Needs reviewer attention"
        if area == "Comparator" and any(x in context for x in ["control", "untreated", "placebo", "baseline"]): status = "Context suggests comparator; verify explicitly"
        elif area == "Replication" and any(x in context for x in ["replicate", "replication", "n="]): status = "Replication mentioned; verify independence"
        elif area == "Novelty" and any(x in context for x in ["novel", "first", "new", "innovative"]): status = "Novelty claim detected; verify against closest literature"
        rows.append({"Attack area": area, "Reviewer challenge": question, "Severity": severity, "Status": status})
    return rows

def attack_score(rows: list[dict[str, str]], resolved: set[str] | None = None) -> dict[str, Any]:
    resolved = resolved or set()
    total = len(rows)
    done = sum(r["Attack area"] in resolved for r in rows)
    return {"total": total, "resolved": done, "open": total-done, "readiness_percent": round(100*done/total, 1) if total else 0.0}
