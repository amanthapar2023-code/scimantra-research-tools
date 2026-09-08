"""Evidence-aware research audit helpers.

These functions intentionally generate audit questions and candidate flags,
not scientific facts. They are designed to sit between planning and verified
analysis in SciMantra.
"""
from __future__ import annotations

import re
from collections import Counter


CAUSAL_WORDS = {"effect", "impact", "influence", "improves", "reduces", "increases", "causes", "enhances"}
COMPARISON_WORDS = {"versus", "vs", "compared", "comparison", "control", "treatment"}
QUANT_WORDS = {"concentration", "rate", "efficiency", "yield", "removal", "activity", "growth", "response"}


def audit_title(title: str) -> dict:
    words = set(re.findall(r"[a-zA-Z0-9]+", title.lower()))
    causal = bool(words & CAUSAL_WORDS)
    comparison = bool(words & COMPARISON_WORDS)
    quantitative = bool(words & QUANT_WORDS)
    flags = []
    if causal:
        flags.append(("Causality", "The title implies an effect. Ensure the design can distinguish causation from association and define the comparison/control."))
    if comparison:
        flags.append(("Comparator", "Identify the exact comparator, baseline or control condition and define it before analysis."))
    if quantitative:
        flags.append(("Primary endpoint", "Define one primary measurable endpoint, its unit, timing and calculation formula."))
    if len(words) < 7:
        flags.append(("Specificity", "The title is broad. Define system/material, intervention/exposure, endpoint and context where appropriate."))
    flags.extend([
        ("Replication", "Record the independent experimental unit and number of independent replicates; technical repeats are not automatically biological replicates."),
        ("Confounding", "List plausible confounders and decide how they will be controlled, measured or acknowledged."),
        ("Alternative explanation", "Write at least one competing explanation for the expected finding and identify an observation that could distinguish it."),
        ("Missing-data plan", "Predefine how missing observations, failed runs and protocol deviations will be documented and handled."),
        ("Analysis lock", "Predefine primary outcomes, transformations and statistical tests before inspecting outcome differences when feasible."),
        ("Traceability", "Every final number and figure should be traceable to raw data and an analysis step."),
    ])
    return {"flags": flags, "causal": causal, "comparison": comparison, "quantitative": quantitative}


def claim_check(claim: str) -> dict:
    """Classify a manuscript claim into an audit checklist; no truth judgement."""
    text = claim.strip()
    lower = text.lower()
    evidence = "high" if any(x in lower for x in ["we found", "our results", "significant", "increased", "decreased"]) else "unknown"
    checks = ["Is the claim directly supported by a reported result?", "Can the reader trace it to a figure/table/data record?", "Does the wording exceed the study design (e.g. causal language from observational data)?", "Are uncertainty and relevant limitations represented?"]
    return {"claim": text, "evidence_status": evidence, "checks": checks}


def risk_score(audit: dict, completed: dict[str, bool] | None = None) -> int:
    completed = completed or {}
    total = len(audit["flags"])
    done = sum(bool(completed.get(label)) for label, _ in audit["flags"])
    return round(100 * done / total) if total else 0


def build_reviewer_questions(title: str) -> list[str]:
    audit = audit_title(title)
    base = [
        "What is the single most important unanswered question?",
        "What result would falsify the central hypothesis?",
        "Why is this design preferable to the simplest competing design?",
        "Which control is essential and what would its failure imply?",
        "What is the true independent experimental unit?",
        "Which conclusion cannot be supported by the planned data?",
        "What alternative mechanism could produce the same observed result?",
        "How will reproducibility be demonstrated rather than assumed?",
        "Which limitation would a skeptical reviewer identify first?",
        "Can every major manuscript claim be traced to a source, dataset or analysis output?",
    ]
    if audit["causal"]:
        base.insert(1, "Does the design justify the causal language used in the title and conclusions?")
    if audit["comparison"]:
        base.insert(2, "Is the comparator scientifically meaningful and matched to the treatment/exposure?")
    return base
