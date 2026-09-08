import re
from typing import Dict, List

FIELDS = [
    "Problem", "Challenges", "Research solution", "Technology / approach",
    "Innovation", "Difference from previous work", "Research gap", "Method",
    "Key result", "Limitation", "Evidence location",
]

FIELD_RULES = {
    "Problem": [r"\bproblem\b", r"challenge[s]?\b", r"need for\b", r"remain[s]? unclear\b", r"difficult(y|ies)?\b"],
    "Challenges": [r"challenge[s]?\b", r"limitation[s]?\b", r"difficult(y|ies)?\b", r"barrier[s]?\b", r"constraint[s]?\b"],
    "Research solution": [r"we propose\b", r"we developed\b", r"we present\b", r"we introduce\b", r"this study (aims|presents|develops)\b", r"solution\b"],
    "Technology / approach": [r"algorithm\b", r"model\b", r"method\b", r"framework\b", r"platform\b", r"sensor\b", r"machine learning\b", r"deep learning\b", r"sequencing\b", r"spectroscop\w*\b"],
    "Innovation": [r"novel\b", r"innovative\b", r"first\b", r"new approach\b", r"new method\b", r"novelty\b"],
    "Difference from previous work": [r"unlike\b", r"compared with\b", r"compared to\b", r"previous (studies|work)\b", r"whereas\b", r"in contrast\b"],
    "Research gap": [r"gap\b", r"little is known\b", r"few studies\b", r"limited (research|evidence)\b", r"remains unknown\b", r"poorly understood\b"],
    "Method": [r"methods?\b", r"experimental\b", r"randomi[sz]ed\b", r"samples?\b", r"participants?\b", r"replicates?\b", r"analy[sz]ed\b", r"data (were|was) collected\b"],
    "Key result": [r"results?\b", r"found that\b", r"showed that\b", r"increased\b", r"decreased\b", r"significant\b", r"p\s*[<=>]\s*0?\.\d+", r"confidence interval\b"],
    "Limitation": [r"limitation[s]?\b", r"limited by\b", r"cannot\b", r"could not\b", r"future work\b", r"further research\b"],
}


def _sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def extract_candidates(text: str) -> List[Dict[str, object]]:
    """Surface candidate source sentences; never rewrite them into scientific claims."""
    candidates = []
    for idx, sentence in enumerate(_sentences(text), start=1):
        lower = sentence.lower()
        matched = []
        for field, patterns in FIELD_RULES.items():
            if any(re.search(pattern, lower) for pattern in patterns):
                matched.append(field)
        if matched:
            score = min(0.98, 0.45 + 0.08 * len(matched) + 0.02 * min(len(sentence.split()), 20))
            for field in matched:
                candidates.append({
                    "Field": field,
                    "Candidate excerpt": sentence,
                    "Sentence": idx,
                    "Heuristic confidence": round(score, 2),
                    "Evidence location": f"Sentence {idx}",
                })
    return candidates


def build_extraction_record(title: str, text: str, source_anchor: str = "", evidence_location: str = "") -> Dict[str, str]:
    record = {field: "" for field in FIELDS}
    record["Title"] = title.strip()
    record["Source anchor"] = source_anchor.strip()
    record["Evidence location"] = evidence_location.strip()
    record["Status"] = "Evidence needed"
    return record


def accept_candidate(record: Dict[str, str], field: str, excerpt: str, location: str = "") -> Dict[str, str]:
    if field not in FIELDS or not excerpt.strip():
        return record
    record = dict(record)
    record[field] = excerpt.strip()
    if field == "Evidence location" and location.strip():
        record[field] = location.strip()
    elif location.strip():
        record["Evidence location"] = location.strip()
    record["Status"] = audit_extraction(record)["Status"]
    return record


def audit_extraction(record: Dict[str, str]) -> Dict[str, object]:
    populated = [f for f in FIELDS[:-1] if str(record.get(f, "")).strip()]
    anchored = bool(str(record.get("Source anchor", "")).strip()) and bool(str(record.get("Evidence location", "")).strip())
    if not populated:
        status = "Evidence needed"
    elif anchored:
        status = "Source-anchored"
    else:
        status = "Partial — location needed"
    return {
        "Fields populated": len(populated),
        "Total evidence fields": len(FIELDS) - 1,
        "Coverage %": round(100 * len(populated) / (len(FIELDS) - 1), 1),
        "Source anchored": anchored,
        "Status": status,
    }


def export_extraction(records: List[Dict[str, str]]) -> str:
    headers = ["Title", "Source anchor"] + FIELDS + ["Status"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for record in records:
        lines.append("| " + " | ".join(str(record.get(h, "")).replace("|", "\\|").replace("\n", " ") for h in headers) + " |")
    return "\n".join(lines)
