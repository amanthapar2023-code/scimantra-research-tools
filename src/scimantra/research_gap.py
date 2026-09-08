from typing import Dict, List

DIMENSIONS = ["Evidence gap", "Method gap", "Population/context gap", "Technology gap", "Outcome gap", "Reproducibility gap", "Comparison gap"]


def _text(record: Dict, fields: List[str]) -> str:
    return " ".join(str(record.get(f, "")).strip() for f in fields if str(record.get(f, "")).strip())


def generate_gap_candidates(records: List[Dict], research_title: str = "") -> List[Dict]:
    """Generate reviewable gap hypotheses from missing/uneven evidence. Never assert a gap as fact."""
    records = [r for r in records if isinstance(r, dict)]
    n = len(records)
    if not n:
        return []
    specs = [
        ("Evidence gap", ["Research gap", "Key result"], "Several papers lack explicit gap/result evidence; verify whether the literature synthesis is incomplete."),
        ("Method gap", ["Method", "Challenges"], "Methods are not consistently documented across the comparison set; inspect whether an important method remains under-tested."),
        ("Population/context gap", ["Problem", "Method", "Limitation"], "Context and study-boundary information may be uneven; check whether an important population, setting, or condition is missing."),
        ("Technology gap", ["Technology / approach", "Innovation"], "Technology/approach coverage is uneven; investigate whether a promising approach has not been tested in the target context."),
        ("Outcome gap", ["Key result", "Research solution"], "Outcome evidence is incomplete; determine whether an important endpoint has not been adequately evaluated."),
        ("Reproducibility gap", ["Method", "Limitation"], "Method/limitation evidence is incomplete; inspect whether reproducibility information is insufficient for replication."),
        ("Comparison gap", ["Difference from previous work", "Key result"], "Direct comparative evidence is limited; verify whether competing approaches have been evaluated under comparable conditions."),
    ]
    rows = []
    for dim, fields, rationale in specs:
        missing = sum(not _text(r, fields) for r in records)
        score = round(100 * missing / n, 1)
        if score == 0:
            signal = "Low signal — evidence present in all supplied records"
        elif score < 50:
            signal = "Moderate signal — partial evidence coverage"
        else:
            signal = "High signal — substantial evidence coverage missing"
        rows.append({"Gap dimension": dim, "Signal score": score, "Papers needing verification": missing, "Signal": signal, "Why investigate": rationale, "Candidate research question": "What remains unresolved in this dimension for the target research context?", "Possible next study": "Define a focused comparison or experiment that directly tests the unresolved question."})
    return sorted(rows, key=lambda x: x["Signal score"], reverse=True)


def rank_gap_candidates(rows: List[Dict], novelty_risk: float = 0.0) -> List[Dict]:
    """Rank gap hypotheses for human review; novelty_risk is a caution signal, not a novelty claim."""
    out = []
    for row in rows:
        score = max(0.0, min(100.0, float(row.get("Signal score", 0))))
        adjusted = round(max(0.0, score - 0.25 * max(0.0, min(100.0, novelty_risk))), 1)
        item = dict(row)
        item["Review priority"] = adjusted
        item["Priority"] = "High" if adjusted >= 60 else "Medium" if adjusted >= 30 else "Low"
        out.append(item)
    return sorted(out, key=lambda x: x["Review priority"], reverse=True)


def gap_validation_checklist(row: Dict) -> List[str]:
    dim = row.get("Gap dimension", "this gap")
    return [
        f"Verify the {dim.lower()} signal against the original papers.",
        "Confirm that the apparent absence is not caused by incomplete searching or extraction.",
        "Check recent and directly comparable studies before claiming novelty.",
        "Define the exact unresolved question rather than using 'no studies exist'.",
        "Specify what observation or experiment could falsify the proposed research direction.",
        "Record supporting citations and evidence locations before writing the Introduction.",
    ]


def export_gap_candidates(rows: List[Dict]) -> str:
    lines = ["# SciMantra Research-Gap Candidates", "", "> These are evidence-derived hypotheses for researcher verification, not claims of novelty or proof that a gap exists.", ""]
    for i, row in enumerate(rows, 1):
        lines += [f"## {i}. {row.get('Gap dimension','Gap')}", f"- Review priority: {row.get('Priority','—')} ({row.get('Review priority','—')})", f"- Signal: {row.get('Signal','—')}", f"- Candidate research question: {row.get('Candidate research question','—')}", f"- Possible next study: {row.get('Possible next study','—')}", "- Validation checklist:"]
        lines += [f"  - {item}" for item in gap_validation_checklist(row)]
        lines.append("")
    return "\n".join(lines)
