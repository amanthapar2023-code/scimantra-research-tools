"""Journal and reviewer requirements auditor for SciMantra."""
from __future__ import annotations
from typing import Any

REQUIREMENTS = [
    ("Manuscript title", "title"), ("Abstract", "abstract"), ("Keywords", "keywords"),
    ("Introduction", "introduction"), ("Methods", "methods"), ("Results", "results"),
    ("Discussion", "discussion"), ("Conclusion", "conclusion"), ("Figures/Tables", "figures_tables"),
    ("References", "references"), ("Data availability", "data_availability"),
    ("Code availability", "code_availability"), ("Ethics statement", "ethics"),
    ("Conflict of interest", "conflict"), ("Supplementary material", "supplementary"),
]
STATUSES = ["Not checked", "Present", "Needs revision", "Not applicable"]

def audit(requirements: dict[str, str], word_count: int = 0, word_limit: int = 0) -> dict[str, Any]:
    missing = [label for label, key in REQUIREMENTS if requirements.get(key, "Not checked") == "Not checked"]
    revision = [label for label, key in REQUIREMENTS if requirements.get(key) == "Needs revision"]
    present = [label for label, key in REQUIREMENTS if requirements.get(key) == "Present"]
    limit_ok = not word_limit or word_count <= word_limit
    return {"total": len(REQUIREMENTS), "present": len(present), "missing": missing, "revision": revision, "word_limit_ok": limit_ok, "ready": not missing and not revision and limit_ok}

def next_actions(result: dict[str, Any]) -> list[str]:
    actions = [f"Complete requirement: {x}" for x in result["missing"]]
    actions += [f"Revise requirement: {x}" for x in result["revision"]]
    if not result["word_limit_ok"]: actions.insert(0, "Reduce manuscript length to meet the configured word limit.")
    return actions
