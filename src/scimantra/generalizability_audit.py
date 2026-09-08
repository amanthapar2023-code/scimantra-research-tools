"""Generalizability / external-validity audit for researcher-defined claims."""
from __future__ import annotations
from typing import Any

DOMAINS = [
    ("Population / sample", "Is the target population represented by the studied sample?"),
    ("Organism / model system", "Does the model justify extension to the intended biological or technical system?"),
    ("Geography / setting", "Are location, institution, field, laboratory, or service settings comparable?"),
    ("Environment / conditions", "Are temperature, medium, habitat, equipment, or operating conditions comparable?"),
    ("Exposure / dose / range", "Does the tested range cover the range implied by the claim?"),
    ("Time / duration", "Is the observation period adequate for the claimed time horizon?"),
    ("Measurement method", "Will the outcome be measured equivalently outside the study context?"),
    ("Selection / inclusion", "Could selection criteria limit who or what the result applies to?"),
    ("Replication / sites", "Has the result been examined across independent samples, batches, operators, or sites?"),
    ("Comparator / context", "Is the reference condition appropriate for the intended application?"),
]

LEVELS = ["Not assessed", "Supported", "Partially supported", "Limited", "Contradicted"]

def template_rows() -> list[dict[str, Any]]:
    return [{"Domain": d, "Question": q, "Status": "Not assessed", "Study context": "", "Target context": "", "Evidence / notes": ""} for d, q in DOMAINS]

def audit_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {x: 0 for x in LEVELS}
    for r in rows: counts[str(r.get("Status", "Not assessed"))] = counts.get(str(r.get("Status", "Not assessed")), 0) + 1
    assessed = len(rows) - counts["Not assessed"]
    favorable = counts["Supported"] + 0.5 * counts["Partially supported"]
    score = round(100 * favorable / assessed, 1) if assessed else 0.0
    return {**counts, "assessed": assessed, "score": score}

def priority_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    weight = {"Contradicted": 100, "Limited": 80, "Partially supported": 55, "Not assessed": 35, "Supported": 0}
    out = []
    for r in rows:
        status = str(r.get("Status", "Not assessed"))
        out.append({"Priority": weight.get(status, 35), "Domain": r.get("Domain", ""), "Status": status, "Action": "Define boundary or collect cross-context evidence" if status in {"Contradicted", "Limited"} else "Assess with evidence" if status == "Not assessed" else "Document why extension is reasonable"})
    return sorted(out, key=lambda x: x["Priority"], reverse=True)

def export_audit(rows: list[dict[str, Any]], audit: dict[str, Any]) -> str:
    lines = ["# SciMantra Generalizability & External Validity Audit", "", f"Planning score among assessed domains: {audit['score']}/100", "", "> Structured audit only. It does not prove that a finding generalizes to a new population, site, condition, or application.", ""]
    for r in rows:
        lines += [f"## {r['Domain']} — {r['Status']}", f"- Question: {r['Question']}", f"- Study context: {r.get('Study context','')}", f"- Target context: {r.get('Target context','')}", f"- Evidence / notes: {r.get('Evidence / notes','')}", ""]
    return "\n".join(lines)
