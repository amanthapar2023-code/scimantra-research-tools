"""Falsification and alternative-hypothesis planning tools.

This module generates candidate explanations and discriminating tests for
research planning. It does not determine which explanation is true.
"""

from __future__ import annotations

from typing import Dict, List


ALTERNATIVE_TEMPLATES = [
    (
        "Measurement artifact",
        "The observed pattern could arise from the measurement, assay, instrument, or endpoint rather than the proposed mechanism.",
        "Repeat or cross-check the outcome with an independent measurement method and predefined quality controls.",
        "The pattern would weaken if it disappears or changes materially under an independent, validated measurement.",
    ),
    (
        "Confounding variable",
        "A third variable associated with both the primary factor and outcome could explain the observed pattern.",
        "Measure plausible confounders prospectively and use blocking, matching, adjustment, or stratification where justified.",
        "The association would weaken after credible control of the confounder.",
    ),
    (
        "Baseline imbalance",
        "Pre-existing differences between groups or experimental units could account for the apparent effect.",
        "Record baseline characteristics before intervention and use a prespecified balance or baseline-adjusted analysis when appropriate.",
        "The pattern would weaken when baseline differences are controlled or balanced.",
    ),
    (
        "Batch or time effect",
        "A batch, operator, instrument, day, location, or temporal effect could track with the primary factor.",
        "Randomize or block across batches/time points and include batch/time provenance in the analysis plan.",
        "The pattern would weaken or fail to replicate across independently randomized batches or time periods.",
    ),
    (
        "Selection or attrition",
        "Who enters, remains in, or is excluded from the analysis could create the observed pattern.",
        "Predefine inclusion/exclusion and missing-data rules, record attrition, and compare relevant sensitivity analyses.",
        "The conclusion would materially change under credible alternative handling of selection or missingness.",
    ),
    (
        "Nonlinear or threshold response",
        "The relationship may be nonlinear, threshold-dependent, saturated, or otherwise different from the assumed directional model.",
        "Use prespecified dose/concentration/time levels that can distinguish competing response shapes and test the functional form.",
        "A response shape inconsistent with the primary directional model would challenge the hypothesis.",
    ),
    (
        "Association without the proposed causation",
        "The factor and outcome may co-vary without the proposed factor producing the outcome.",
        "Use a stronger comparator, temporal ordering, intervention, negative control, or other design feature appropriate to the causal question.",
        "Failure of the causal intervention or a credible negative-control pattern would weaken the causal interpretation.",
    ),
]


def _clean(value: str, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def generate_alternatives(
    hypothesis: str,
    factor: str = "the primary factor",
    outcome: str = "the primary outcome",
    comparator: str = "the comparator",
    observed_pattern: str = "the observed pattern",
) -> List[Dict[str, str]]:
    """Create candidate alternative explanations without asserting any are true."""
    hypothesis = _clean(hypothesis, "the primary hypothesis")
    factor = _clean(factor, "the primary factor")
    outcome = _clean(outcome, "the primary outcome")
    comparator = _clean(comparator, "the comparator")
    observed_pattern = _clean(observed_pattern, "the observed pattern")

    rows: List[Dict[str, str]] = []
    for name, explanation, test, falsifier in ALTERNATIVE_TEMPLATES:
        rows.append(
            {
                "Alternative explanation": name,
                "Candidate rationale": explanation,
                "Primary hypothesis": hypothesis,
                "What it could explain": observed_pattern,
                "Discriminating test": test,
                "Hypothetical pattern supporting alternative": falsifier,
                "Primary factor": factor,
                "Primary outcome": outcome,
                "Comparator": comparator,
                "Control / measurement needed": "Researcher to specify",
                "Falsification status": "Unresolved",
                "Researcher decision / reason": "",
            }
        )
    return rows


def audit_falsification(rows: List[Dict[str, str]]) -> Dict[str, object]:
    """Audit whether candidate alternatives have actionable discrimination plans."""
    checks = [
        ("Alternative explanation", "Alternative explanation identified"),
        ("Discriminating test", "Discriminating test defined"),
        ("Primary outcome", "Measurable outcome specified"),
        ("Comparator", "Comparator/context specified"),
        ("Control / measurement needed", "Control or measurement plan specified"),
        ("Researcher decision / reason", "Researcher decision documented"),
    ]
    total = len(rows) * len(checks)
    complete = 0
    for row in rows:
        for field, _ in checks:
            value = str(row.get(field, "")).strip()
            if value and value.lower() != "researcher to specify":
                complete += 1
    score = round(100 * complete / total, 1) if total else 0.0
    unresolved = sum(1 for row in rows if row.get("Falsification status", "Unresolved") == "Unresolved")
    return {
        "alternatives": len(rows),
        "check_items": total,
        "completed_items": complete,
        "audit_score": score,
        "unresolved": unresolved,
        "interpretation": "Planning-ready" if score >= 80 else "Needs researcher review",
    }


def rank_discriminating_tests(rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    """Rank tests using transparent planning heuristics, not scientific certainty."""
    ranked = []
    for row in rows:
        text = " ".join(str(row.get(k, "")) for k in ("Discriminating test", "Control / measurement needed"))
        score = 0
        if row.get("Discriminating test", "").strip():
            score += 50
        if row.get("Control / measurement needed", "").strip() not in ("", "Researcher to specify"):
            score += 25
        if any(term in text.lower() for term in ("independent", "random", "control", "negative", "block")):
            score += 25
        ranked.append({"Alternative explanation": row.get("Alternative explanation", ""), "Test priority": score, "Discriminating test": row.get("Discriminating test", "")})
    return sorted(ranked, key=lambda x: (-int(x["Test priority"]), str(x["Alternative explanation"])))


def export_falsification(rows: List[Dict[str, str]], audit: Dict[str, object]) -> str:
    lines = [
        "# Falsification & Alternative-Hypothesis Lab",
        "",
        "> Planning artifact only. Candidate alternatives and hypothetical patterns are not experimental evidence.",
        "",
        f"Audit score: {audit.get('audit_score', 0)}%",
        f"Alternatives: {audit.get('alternatives', 0)}",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row.get('Alternative explanation', '')}",
                f"- Candidate rationale: {row.get('Candidate rationale', '')}",
                f"- Discriminating test: {row.get('Discriminating test', '')}",
                f"- Hypothetical pattern: {row.get('Hypothetical pattern supporting alternative', '')}",
                f"- Control / measurement: {row.get('Control / measurement needed', '')}",
                f"- Status: {row.get('Falsification status', 'Unresolved')}",
                f"- Researcher decision: {row.get('Researcher decision / reason', '')}",
                "",
            ]
        )
    return "\n".join(lines)
