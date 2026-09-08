"""Methodology Designer and Experimental Design Auditor.

Creates an editable study-design specification from a research title. It is a
planning/audit tool, not a substitute for domain expertise or ethics review.
It deliberately avoids inventing sample sizes, results, or scientific facts.
"""
from __future__ import annotations

from typing import Any


def design_from_title(title: str) -> dict[str, Any]:
    t = title.strip() or "the proposed study"
    return {
        "study_question": f"What measurable effect or relationship will be tested in {t}?",
        "design_type": "Select: controlled experiment / observational study / diagnostic validation / modeling / systematic review",
        "primary_outcome": "Define one primary outcome before data collection.",
        "secondary_outcomes": "List secondary outcomes and distinguish exploratory outcomes.",
        "intervention": "Define the exposure, intervention, technology, treatment, or predictor precisely.",
        "comparator": "Define untreated/control, baseline, benchmark, or alternative-method comparator.",
        "experimental_unit": "Define the true independent experimental unit; do not confuse technical replicates with biological/independent replicates.",
        "factors": "List independent variables/factors and their levels or measurement ranges.",
        "confounders": "List plausible confounders and how they will be controlled, randomized, blocked, matched, or adjusted.",
        "replication": "Pre-specify independent replication and justify it with the intended analysis/power calculation.",
        "randomization": "State whether and how allocation/order will be randomized.",
        "blinding": "State who, if anyone, can be blinded and how outcome assessment will be protected from bias.",
        "sampling": "Define population, inclusion/exclusion criteria, sampling frame, and sampling schedule.",
        "measurement": "Define instruments, units, calibration/QC, detection limits, and measurement timing.",
        "analysis": "Pre-specify primary comparison/model, effect size, uncertainty interval, assumptions, and missing-data handling.",
        "robustness": "Plan sensitivity/robustness checks and identify conditions under which the conclusion could change.",
        "reproducibility": "Record protocol version, raw data, metadata, code, software versions, and deviations.",
    }


def audit_design(design: dict[str, Any]) -> list[dict[str, str]]:
    checks = [
        ("Primary outcome", "primary_outcome", "A primary endpoint is explicitly defined."),
        ("Comparator", "comparator", "A defensible comparator or benchmark is specified."),
        ("Experimental unit", "experimental_unit", "Independence is defined at the correct experimental-unit level."),
        ("Replication", "replication", "Independent replication is planned and justified."),
        ("Randomization", "randomization", "Allocation or measurement order is addressed."),
        ("Blinding", "blinding", "Blinding or objective outcome assessment is addressed."),
        ("Confounding", "confounders", "Plausible confounders and mitigation are addressed."),
        ("Measurement QC", "measurement", "Measurement quality, units and calibration are specified."),
        ("Analysis lock", "analysis", "The main analysis and uncertainty reporting are pre-specified."),
        ("Missing data", "analysis", "A missing-data strategy is explicitly described."),
        ("Reproducibility", "reproducibility", "Raw data, metadata, protocol and analysis traceability are planned."),
    ]
    out = []
    for label, key, requirement in checks:
        value = str(design.get(key, "")).strip()
        out.append({"Check": label, "Status": "ADD DETAIL" if not value or value.startswith("Define") or value.startswith("List") or value.startswith("State") or value.startswith("Plan") or value.startswith("Record") else "PRESENT", "Requirement": requirement})
    return out


def design_score(audit: list[dict[str, str]]) -> dict[str, float]:
    total = len(audit)
    present = sum(x["Status"] == "PRESENT" for x in audit)
    return {"score": round(100 * present / total, 1) if total else 0.0, "present": present, "total": total}


def reviewer_challenges(design: dict[str, Any]) -> list[str]:
    return [
        "What is the true independent experimental unit, and could pseudoreplication inflate the apparent sample size?",
        "What comparator would demonstrate that the observed effect is attributable to the proposed approach rather than time, handling, or baseline differences?",
        "Which confounder or alternative explanation is most capable of reversing the conclusion?",
        "Were primary and secondary outcomes defined before inspecting the results?",
        "Is the planned replication sufficient for the intended effect-size estimate and uncertainty?",
        "Could measurement error, batch effects, instrument drift, or operator effects explain part of the observed signal?",
        "How will missing observations and protocol deviations be handled without selectively removing inconvenient data?",
        "Can another researcher reproduce the analysis from the raw data and recorded protocol?",
    ]
