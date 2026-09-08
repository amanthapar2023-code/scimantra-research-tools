"""Machine-readable reproducibility passport for a research project."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

SECTIONS = [
    ("Research identity", "Title, question, objectives, hypotheses"),
    ("Protocol", "Design, experimental unit, controls, replication, randomization, blinding"),
    ("Data provenance", "Raw-data source, acquisition date, identifiers, transformations"),
    ("Analysis", "Software, versions, scripts, statistical methods, locked decisions"),
    ("Figures and tables", "Source dataset, generation settings, units, resolution"),
    ("Evidence", "Literature sources, evidence locations, claim links"),
    ("Exceptions", "Deviations, exclusions, failed runs, missing data and reasons"),
    ("Reproducibility", "Files, environment, dependencies, checksums or persistent identifiers"),
]

def passport_template(title: str = "") -> dict[str, Any]:
    return {"passport_version": "1.0", "created_utc": datetime.now(timezone.utc).isoformat(), "research_title": title, "sections": {name: {"description": desc, "status": "MISSING", "record": ""} for name, desc in SECTIONS}}

def passport_audit(passport: dict[str, Any]) -> dict[str, Any]:
    sections = passport.get("sections", {})
    total = len(SECTIONS)
    complete = sum(str(v.get("record", "")).strip() != "" for v in sections.values())
    return {"total_sections": total, "complete_sections": complete, "missing_sections": total-complete, "coverage_percent": round(100*complete/total, 1) if total else 0.0}

def export_markdown(passport: dict[str, Any]) -> str:
    lines = ["# Research Reproducibility Passport", "", f"**Title:** {passport.get('research_title','')}", f"**Passport version:** {passport.get('passport_version','1.0')}", f"**Created (UTC):** {passport.get('created_utc','')}", ""]
    for name, data in passport.get("sections", {}).items():
        lines += [f"## {name}", data.get("description", ""), "", data.get("record", "[MISSING]"), ""]
    return "\n".join(lines)
