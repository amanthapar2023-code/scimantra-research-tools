"""Evidence-aware bridge from computed results to Results/Discussion planning."""
from __future__ import annotations

from typing import Any


def result_statements(comparison: dict[str, Any]) -> list[str]:
    if comparison.get("status") != "OK":
        return ["No two-group result statement can be generated until valid group data are supplied."]
    a, b = comparison["group_a"], comparison["group_b"]
    return [
        f"Observed-data statement: {a} mean = {comparison['mean_a']:.4g}; {b} mean = {comparison['mean_b']:.4g}; observed difference = {comparison['difference']:.4g}.",
        "Interpretive statement: determine whether this observed difference is compatible with the pre-specified hypothesis and analysis assumptions.",
        "Causal statement: do not write a causal conclusion unless the study design and analysis support causal inference.",
    ]


def discussion_prompts(comparison: dict[str, Any], hypothesis: str = "") -> list[str]:
    prompts = [
        "What does the observed effect mean in the context of the primary research question?",
        "Does the direction and magnitude of the effect agree with the pre-specified hypothesis?",
        "Which literature evidence supports, contradicts, or qualifies this interpretation?",
        "What alternative mechanism or confounder could produce the same pattern?",
        "How do replication, uncertainty, measurement quality, and experimental-unit definition affect confidence?",
        "What is the practical or biological relevance of the effect, beyond statistical significance?",
        "Which limitation most constrains generalization of the finding?",
        "What experiment would most efficiently discriminate between competing explanations?",
    ]
    if hypothesis.strip():
        prompts.insert(1, f"Hypothesis supplied by researcher: {hypothesis.strip()}")
    return prompts


def claim_levels() -> list[dict[str, str]]:
    return [
        {"Level": "Observed", "Rule": "Directly report a value calculated from the supplied dataset."},
        {"Level": "Statistical", "Rule": "Report an analysis result only when the relevant test/model has actually been run."},
        {"Level": "Mechanistic", "Rule": "Requires evidence that distinguishes the proposed mechanism from alternatives."},
        {"Level": "Causal", "Rule": "Requires a design and assumptions that justify causal inference."},
        {"Level": "Generalized", "Rule": "Requires evidence that the sampled conditions support the intended scope of generalization."},
    ]
