"""Evidence-grounded Introduction Architect and Research Gap Engine.

This module turns researcher-verified literature-matrix fields into a transparent
writing blueprint. It deliberately avoids fabricating claims, results, or gaps.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


INTRO_SECTIONS = [
    ("Problem", "Establish the real-world/scientific problem and why it matters."),
    ("Challenges", "Show the unresolved technical, biological, methodological, or practical challenges."),
    ("Previous research", "Synthesize what the selected studies actually attempted and how."),
    ("Technology / approach", "Compare the technologies or approaches used across the evidence set."),
    ("What is still missing", "Move from repeated limitations and inconsistencies toward the defensible gap."),
    ("Proposed direction", "State the study's intended contribution without inventing results."),
    ("Study objective", "State the primary objective and testable questions."),
]


def _text(records: Iterable[dict[str, str]], field: str) -> list[str]:
    return [str(r.get(field, "")).strip() for r in records if str(r.get(field, "")).strip()]


def _terms(values: Iterable[str], limit: int = 12) -> list[tuple[str, int]]:
    stop = {"the", "and", "for", "with", "from", "that", "this", "were", "was", "are", "using", "used", "into", "their", "study", "research", "method", "based", "have", "has", "than", "which", "also", "not", "can"}
    words: list[str] = []
    for value in values:
        words.extend(re.findall(r"[A-Za-z][A-Za-z-]{3,}", value.lower()))
    return Counter(w for w in words if w not in stop).most_common(limit)


def _paper_refs(records: list[dict[str, str]], field: str) -> list[str]:
    refs = []
    for r in records:
        if str(r.get(field, "")).strip():
            refs.append(str(r.get("Paper", "Unnamed paper")).strip() or "Unnamed paper")
    return refs


def gap_engine(records: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Produce candidate gap patterns with transparent evidence requirements."""
    out: list[dict[str, str]] = []
    n = max(len(records), 1)

    limitation = _text(records, "Limitation")
    if limitation:
        out.append({"type": "Repeated limitation", "finding": f"{len(limitation)}/{n} papers report a limitation.", "evidence": "; ".join(limitation[:4]), "action": "Check whether the limitation recurs across independent studies before treating it as a field-level gap."})

    gaps = _text(records, "Research gap")
    if gaps:
        out.append({"type": "Explicitly stated gaps", "finding": f"{len(gaps)}/{n} papers contain a research-gap statement.", "evidence": "; ".join(gaps[:4]), "action": "Compare the wording and scope of these gaps; do not merge them into one claim without source support."})

    methods = _text(records, "Method")
    if methods:
        common = _terms(methods, 5)
        if common:
            out.append({"type": "Method concentration", "finding": "Repeated method terminology appears in the matrix.", "evidence": ", ".join(f"{w} ({c})" for w, c in common), "action": "Ask whether an alternative method, validation setting, control, or mechanism test is absent and verify it in full text."})

    tech = _text(records, "Technology / approach")
    if tech:
        common = _terms(tech, 5)
        if common:
            out.append({"type": "Approach pattern", "finding": "Technology/approach terminology is concentrated across the selected papers.", "evidence": ", ".join(f"{w} ({c})" for w, c in common), "action": "Investigate whether the dominant approach leaves a measurable performance, scalability, mechanism, or validation question."})

    missing_controls = sum(not str(r.get("Difference from previous work", "")).strip() for r in records)
    if missing_controls:
        out.append({"type": "Comparison evidence gap", "finding": f"{missing_controls}/{n} papers lack structured comparison with previous work.", "evidence": "No comparative detail entered for these records.", "action": "Extract explicit comparators, baselines, controls, or prior-work differences from the papers."})

    unanchored = sum(not str(r.get("Evidence location", "")).strip() for r in records)
    if unanchored:
        out.append({"type": "Provenance gap", "finding": f"{unanchored}/{n} papers have no evidence location recorded.", "evidence": "Section/page/table/figure/DOI location is missing.", "action": "Anchor claims before using them in the Introduction."})

    return {"candidate_gaps": out}


def build_introduction_blueprint(title: str, records: list[dict[str, str]]) -> dict[str, object]:
    gap = gap_engine(records)
    sections = []
    for name, purpose in INTRO_SECTIONS:
        fields = {
            "Problem": ["Problem"],
            "Challenges": ["Challenges"],
            "Previous research": ["Research solution", "Difference from previous work"],
            "Technology / approach": ["Technology / approach", "Method"],
            "What is still missing": ["Limitation", "Research gap"],
            "Proposed direction": ["Innovation"],
            "Study objective": [],
        }[name]
        evidence = []
        source_papers = set()
        for field in fields:
            for r in records:
                value = str(r.get(field, "")).strip()
                if value:
                    evidence.append({"field": field, "text": value, "paper": r.get("Paper", "Unnamed paper"), "location": r.get("Evidence location", "")})
                    source_papers.add(r.get("Paper", "Unnamed paper"))
        sections.append({"section": name, "purpose": purpose, "evidence": evidence, "source_papers": sorted(p for p in source_papers if p)})

    result_present = bool(_text(records, "Key result"))
    return {
        "title": title.strip(),
        "sections": sections,
        "candidate_gaps": gap["candidate_gaps"],
        "result_evidence_present": result_present,
        "result_rule": "Only insert Key result statements after researcher verification and source anchoring." if result_present else "No verified results were supplied. Results/Discussion must remain a future-work placeholder.",
    }


def render_markdown(blueprint: dict[str, object]) -> str:
    lines = [f"# Introduction Blueprint — {blueprint.get('title', '')}", "", "Evidence-first drafting plan. Replace each evidence block with your own synthesis and citation.", ""]
    for section in blueprint["sections"]:  # type: ignore[index]
        lines += [f"## {section['section']}", section["purpose"]]
        evidence = section["evidence"]
        if evidence:
            for item in evidence:
                loc = f" — {item['location']}" if item["location"] else " — LOCATION NEEDED"
                lines.append(f"- [{item['paper']}] {item['text']}{loc}")
        else:
            lines.append("- Evidence not supplied; do not invent content.")
        lines.append("")
    lines += ["## Candidate research gaps", ""]
    for item in blueprint["candidate_gaps"]:  # type: ignore[index]
        lines += [f"### {item['type']}", f"**Pattern:** {item['finding']}", f"**Evidence:** {item['evidence']}", f"**Next verification:** {item['action']}", ""]
    lines += ["## Integrity rule", blueprint["result_rule"]]
    return "\n".join(lines)
