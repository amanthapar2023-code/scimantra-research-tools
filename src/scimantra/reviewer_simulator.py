"""Structured hostile peer-review simulator for research manuscripts."""
from __future__ import annotations
from typing import Any

CATEGORIES = ["Study design", "Sample size", "Controls", "Statistics", "Causality", "Mechanism", "Novelty", "Evidence", "Generalizability", "Reproducibility", "Writing / claim scope", "Reporting"]
SEVERITIES = ["Not assessed", "Low", "Moderate", "High", "Critical"]

PROMPTS = {
    "Study design": "Is the design appropriate for the exact research question and inference?",
    "Sample size": "Is the sample size, replication structure, and experimental unit adequate?",
    "Controls": "Are the positive, negative, vehicle, baseline, or comparator controls sufficient?",
    "Statistics": "Are the statistical methods, assumptions, multiplicity, and effect reporting appropriate?",
    "Causality": "Does the manuscript claim causation when the design may only support association?",
    "Mechanism": "Is the proposed mechanism directly supported or mainly inferred from downstream observations?",
    "Novelty": "Is the claimed novelty clearly differentiated from prior work?",
    "Evidence": "Can each major conclusion be traced to adequate primary evidence?",
    "Generalizability": "Are conclusions extended beyond the studied population or conditions?",
    "Reproducibility": "Are methods, data-processing decisions, software, and materials sufficiently documented?",
    "Writing / claim scope": "Does the wording exceed what the evidence can support?",
    "Reporting": "Are important exclusions, missing data, limitations, negative results, and analysis choices transparent?",
}

def template():
    return [{"Category": c, "Severity": "Not assessed", "Reviewer challenge": PROMPTS[c], "Evidence / manuscript location": "", "Author response": "", "Revision made": "", "Resolved": "No"} for c in CATEGORIES]

def audit(rows):
    weights = {"Critical": 100, "High": 75, "Moderate": 45, "Low": 15, "Not assessed": 30}
    return {"items": len(rows), "critical": sum(r.get("Severity") == "Critical" for r in rows), "high": sum(r.get("Severity") == "High" for r in rows), "moderate": sum(r.get("Severity") == "Moderate" for r in rows), "unresolved": sum(r.get("Resolved") != "Yes" for r in rows), "risk": round(sum(weights.get(r.get("Severity"), 30) for r in rows) / len(rows), 1) if rows else 0}

def priority_queue(rows):
    rank = {"Critical": 100, "High": 75, "Moderate": 45, "Low": 15, "Not assessed": 30}
    out = []
    for r in rows:
        severity = r.get("Severity", "Not assessed")
        resolved = r.get("Resolved") == "Yes"
        out.append({"Priority": 0 if resolved else rank.get(severity, 30), "Category": r.get("Category", ""), "Severity": severity, "Resolved": "Yes" if resolved else "No", "Action": "Document evidence and response; revise manuscript if needed" if not resolved else "Keep response and revision trace"})
    return sorted(out, key=lambda x: x["Priority"], reverse=True)

def export_review(rows, summary):
    lines = ["# SciMantra Hostile Peer-Review Simulation", "", f"Reviewer risk index: {summary['risk']}/100", "", "> Simulated reviewer challenges are structured prompts, not predictions of an actual journal decision.", ""]
    for i, r in enumerate(rows, 1):
        lines += [f"## Review point {i} — {r['Severity']}", f"**Challenge:** {r['Reviewer challenge']}", f"**Evidence/location:** {r.get('Evidence / manuscript location','')}", f"**Author response:** {r.get('Author response','')}", f"**Revision made:** {r.get('Revision made','')}", f"**Resolved:** {r.get('Resolved','No')}", ""]
    return "\n".join(lines)
