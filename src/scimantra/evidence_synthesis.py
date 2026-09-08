import re
from collections import Counter
from typing import Dict, List

FIELDS = ["Problem", "Challenges", "Research solution", "Technology / approach", "Innovation", "Difference from previous work", "Research gap", "Method", "Key result", "Limitation"]


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", str(text or "").lower()) if t not in {"the", "and", "for", "with", "from", "that", "this", "were", "was", "are", "using", "into", "their"}}


def _similarity(a: str, b: str) -> float:
    x, y = _tokens(a), _tokens(b)
    return 0.0 if not x or not y else round(len(x & y) / len(x | y), 3)


def normalize_records(records: List[Dict]) -> List[Dict]:
    return [r for r in records if isinstance(r, dict) and any(str(r.get(f, "")).strip() for f in FIELDS)]


def field_coverage(records: List[Dict]) -> List[Dict]:
    records = normalize_records(records)
    n = len(records)
    rows = []
    for field in FIELDS:
        count = sum(bool(str(r.get(field, "")).strip()) for r in records)
        rows.append({"Field": field, "Papers with evidence": count, "Coverage %": round(100 * count / n, 1) if n else 0.0})
    return rows


def contradiction_signals(records: List[Dict]) -> List[Dict]:
    """Flags papers whose result/solution wording has low lexical overlap with peers.
    This is a review prompt, not a scientific contradiction detector."""
    records = normalize_records(records)
    rows = []
    for i, record in enumerate(records):
        text = " ".join(str(record.get(f, "")) for f in ["Research solution", "Key result"])
        if not text:
            continue
        scores = [_similarity(text, " ".join(str(other.get(f, "")) for f in ["Research solution", "Key result"])) for j, other in enumerate(records) if j != i]
        mean_overlap = round(sum(scores) / len(scores), 3) if scores else 0.0
        rows.append({"Paper": record.get("Title", f"Paper {i+1}"), "Peer lexical overlap": mean_overlap, "Review signal": "Potential divergence — inspect source" if mean_overlap < 0.12 and len(scores) else "No automatic divergence signal"})
    return rows


def gap_map(records: List[Dict]) -> List[Dict]:
    records = normalize_records(records)
    rows = []
    for field in ["Research gap", "Limitation", "Difference from previous work", "Method", "Key result"]:
        missing = [str(r.get("Title", f"Paper {i+1}")) for i, r in enumerate(records) if not str(r.get(field, "")).strip()]
        present = len(records) - len(missing)
        if not records:
            signal = "No papers supplied"
        elif present == 0:
            signal = "Unresolved across all supplied records"
        elif present < len(records):
            signal = "Partial evidence — verify missing papers"
        else:
            signal = "Covered — compare evidence for substantive gaps"
        rows.append({"Dimension": field, "Papers with evidence": present, "Missing papers": len(missing), "Signal": signal, "Verification needed": "; ".join(missing[:5])})
    return rows


def theme_frequency(records: List[Dict], field: str = "Technology / approach", limit: int = 15) -> List[Dict]:
    counter = Counter()
    for r in normalize_records(records):
        counter.update(_tokens(r.get(field, "")))
    return [{"Term": term, "Paper-independent text mentions": count} for term, count in counter.most_common(limit)]


def synthesis_summary(records: List[Dict]) -> Dict[str, object]:
    records = normalize_records(records)
    coverage = field_coverage(records)
    overall = round(sum(r["Coverage %"] for r in coverage) / len(coverage), 1) if coverage else 0.0
    return {"Papers": len(records), "Average evidence coverage %": overall, "Strongest dimension": max(coverage, key=lambda x: x["Coverage %"])["Field"] if coverage else "—", "Weakest dimension": min(coverage, key=lambda x: x["Coverage %"])["Field"] if coverage else "—"}


def export_synthesis(summary: Dict, coverage: List[Dict], gaps: List[Dict], divergence: List[Dict]) -> str:
    lines = ["# SciMantra Evidence Synthesis", "", "## Summary"]
    lines += [f"- {k}: {v}" for k, v in summary.items()]
    lines += ["", "## Evidence coverage", "", "| Dimension | Papers with evidence | Coverage % |", "|---|---:|---:|"]
    lines += [f"| {r['Field']} | {r['Papers with evidence']} | {r['Coverage %']} |" for r in coverage]
    lines += ["", "## Gap signals", "", "| Dimension | Papers with evidence | Missing papers | Signal |", "|---|---:|---:|---|"]
    lines += [f"| {r['Dimension']} | {r['Papers with evidence']} | {r['Missing papers']} | {r['Signal']} |" for r in gaps]
    lines += ["", "## Divergence review prompts"]
    lines += [f"- **{r['Paper']}** — {r['Review signal']} (peer lexical overlap: {r['Peer lexical overlap']})" for r in divergence]
    lines += ["", "> Automatic signals are triage aids. They do not establish scientific gaps, contradictions, novelty, or truth."]
    return "\n".join(lines)
