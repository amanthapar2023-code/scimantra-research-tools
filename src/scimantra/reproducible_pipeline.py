"""Machine-readable planning model for reproducible research analysis pipelines."""
from __future__ import annotations
from typing import Dict, List

STEP_TYPES = ["Raw data", "Cleaning", "Exclusion", "Transformation", "Model", "Sensitivity", "Figure", "Table", "Conclusion"]
REQUIRED_FIELDS = ["owner", "input", "output", "rule", "software", "version", "notes"]


def default_steps() -> List[Dict[str, str]]:
    names = [
        ("01", "Raw data", "Dataset received from experiment or source"),
        ("02", "Cleaning", "Quality control and data cleaning"),
        ("03", "Exclusion", "Prespecified exclusion decisions"),
        ("04", "Transformation", "Derived variables and transformations"),
        ("05", "Model", "Primary statistical analysis"),
        ("06", "Sensitivity", "Robustness and alternative analyses"),
        ("07", "Figure", "Publication figure generation"),
        ("08", "Table", "Publication table generation"),
        ("09", "Conclusion", "Evidence-grounded interpretation"),
    ]
    return [{"ID": i, "Type": t, "Name": n, "Status": "Planned", "owner": "", "input": "", "output": "", "rule": "", "software": "", "version": "", "notes": ""} for i, t, n in names]


def audit_pipeline(steps: List[Dict[str, str]]) -> Dict[str, object]:
    issues = []
    ids = [str(s.get("ID", "")) for s in steps]
    if len(ids) != len(set(ids)):
        issues.append("Duplicate step IDs")
    for s in steps:
        missing = [f for f in REQUIRED_FIELDS if not str(s.get(f, "")).strip()]
        if missing:
            issues.append(f"{s.get('ID', '?')} {s.get('Type', '')}: missing {', '.join(missing)}")
    types = {str(s.get("Type", "")) for s in steps}
    for required in ["Raw data", "Cleaning", "Model", "Conclusion"]:
        if required not in types:
            issues.append(f"Missing pipeline stage: {required}")
    return {"steps": len(steps), "issues": issues, "complete": not issues, "coverage": round(100 * sum(bool(str(s.get('rule','')).strip()) for s in steps) / len(steps), 1) if steps else 0.0}


def dependency_map(steps: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for i, s in enumerate(steps):
        prev = steps[i - 1]["ID"] if i else "SOURCE"
        out.append({"From": prev, "To": s["ID"], "Stage": s["Type"], "Artifact": s.get("output", "") or "Unspecified"})
    return out


def export_pipeline(steps: List[Dict[str, str]], audit: Dict[str, object]) -> str:
    lines = ["# Reproducible Analysis Pipeline", "", f"Pipeline coverage: {audit['coverage']}%", ""]
    for s in steps:
        lines += [f"## {s['ID']} — {s['Name']}", f"- Type: {s['Type']}", f"- Status: {s['Status']}", f"- Owner: {s['owner']}", f"- Input: {s['input']}", f"- Output: {s['output']}", f"- Rule: {s['rule']}", f"- Software: {s['software']} {s['version']}", f"- Notes: {s['notes']}", ""]
    return "\n".join(lines)
