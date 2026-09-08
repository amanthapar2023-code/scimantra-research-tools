"""Research Claim Stress-Test / Overclaim Detector.

Transparent wording-audit heuristics for manuscript claims. The engine does
not determine scientific truth; it flags language that should be checked
against study design, data, literature, and provenance.
"""
from __future__ import annotations
import re
from typing import Any

CATEGORIES = [
    "Causal overreach", "Mechanistic overreach", "Statistical certainty",
    "Generalization", "Novelty claim", "Evidence / provenance",
    "Conclusion strength", "Quantitative consistency",
]

PATTERNS = {
    "Causal overreach": r"\b(proves?|causes?|caused|lead(s)? to|results? in|responsible for|due to|drives?|determines?)\b",
    "Mechanistic overreach": r"\b(mechanism|mechanistically|via|through|mediated|because|explains?|accounts? for)\b",
    "Statistical certainty": r"\b(definitively|certainly|conclusive|proves?|significant(ly)?\s+demonstrates?|no doubt|establishes?)\b",
    "Generalization": r"\b(all|every|always|never|universally|regardless of|in any|across all|generalizable|generalisable)\b",
    "Novelty claim": r"\b(first|novel|new|unique|unprecedented|for the first time|never previously)\b",
    "Conclusion strength": r"\b(proves?|demonstrates?|confirms?|establishes?|definitively shows?)\b",
}

WEAKENING = {
    "Causal overreach": "consider association / effect wording unless the design supports causality",
    "Mechanistic overreach": "separate observed effect from mechanism unless mechanism was directly tested",
    "Statistical certainty": "report estimate and uncertainty; avoid treating statistical evidence as absolute certainty",
    "Generalization": "limit the claim to the studied population, conditions, time, and measurement scope",
    "Novelty claim": "verify against the closest literature before using priority or originality language",
    "Conclusion strength": "match conclusion strength to the design, evidence, uncertainty, and alternatives",
}

def audit_claim(claim: str, evidence: str = "", design: str = "", source: str = "") -> dict[str, Any]:
    text = str(claim or "").strip()
    flags: list[dict[str, str]] = []
    if not text:
        return {"Claim": "", "Risk level": "High", "Flags": [{"Category": "Empty claim", "Trigger": "No manuscript claim supplied", "Action": "Enter the exact sentence to stress-test."}], "Evidence supplied": bool(str(evidence).strip()), "Design supplied": bool(str(design).strip()), "Source supplied": bool(str(source).strip())}
    for category, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.I)
        if match:
            flags.append({"Category": category, "Trigger": match.group(0), "Action": WEAKENING.get(category, "Verify this wording against the underlying evidence.")})
    if not str(evidence).strip():
        flags.append({"Category": "Evidence / provenance", "Trigger": "No evidence anchor supplied", "Action": "Attach dataset, analysis, figure/table, protocol, or source location."})
    if not str(source).strip() and re.search(r"\b(first|novel|new|unique|unprecedented)\b", text, re.I):
        flags.append({"Category": "Novelty claim", "Trigger": "Novelty language without source anchor", "Action": "Record the closest verified literature used to support the novelty argument."})
    risk = "High" if len(flags) >= 3 else "Moderate" if flags else "Low — no heuristic trigger"
    return {"Claim": text, "Risk level": risk, "Flags": flags, "Evidence supplied": bool(str(evidence).strip()), "Design supplied": bool(str(design).strip()), "Source supplied": bool(str(source).strip())}

def stress_test(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for i, item in enumerate(claims, 1):
        result = audit_claim(item.get("Claim", ""), item.get("Evidence", ""), item.get("Design", ""), item.get("Source", ""))
        rows.append({"ID": item.get("ID", f"C{i}"), "Claim": result["Claim"], "Risk level": result["Risk level"], "Flag count": len(result["Flags"]), "Top flags": "; ".join(f["Category"] for f in result["Flags"][:4]) or "None", "Evidence supplied": result["Evidence supplied"], "Design supplied": result["Design supplied"], "Source supplied": result["Source supplied"]})
    return rows

def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"claims": len(rows), "high": sum(r["Risk level"] == "High" for r in rows), "moderate": sum(r["Risk level"] == "Moderate" for r in rows), "low": sum(r["Risk level"].startswith("Low") for r in rows), "claims_needing_review": sum(r["Risk level"] != "Low — no heuristic trigger" for r in rows)}

def export_stress_test(rows: list[dict[str, Any]], detailed: list[dict[str, Any]] | None = None) -> str:
    lines = ["# SciMantra Research Claim Stress-Test", "", "> Heuristic wording audit. A flag is a prompt for researcher verification, not proof of overclaiming or scientific error.", ""]
    for r in rows:
        lines += [f"## {r['ID']} — {r['Risk level']}", r["Claim"], "", f"- Flags: {r['Top flags']}", f"- Evidence supplied: {r['Evidence supplied']}", f"- Design supplied: {r['Design supplied']}", f"- Source supplied: {r['Source supplied']}", ""]
    return "\n".join(lines)
