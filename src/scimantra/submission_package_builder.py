"""Submission package readiness and manifest builder."""
from __future__ import annotations
from typing import Any

ITEMS = [
    ("Manuscript", "manuscript", True), ("Cover letter", "cover_letter", True),
    ("Figures", "figures", True), ("Tables", "tables", True),
    ("Supplementary files", "supplementary", False), ("References", "references", True),
    ("Data availability statement", "data_statement", True), ("Code availability statement", "code_statement", False),
    ("Ethics statement", "ethics", False), ("Conflict of interest declaration", "conflict", True),
    ("Author contribution statement", "contributions", True), ("Reviewer suggestions", "reviewers", False),
]

def audit(package: dict[str, dict[str, Any]]) -> dict[str, Any]:
    required = [key for _,key,req in ITEMS if req]
    missing = [label for label,key,req in ITEMS if req and not package.get(key,{}).get("ready",False)]
    optional_missing = [label for label,key,req in ITEMS if not req and not package.get(key,{}).get("ready",False)]
    return {"required":len(required),"ready_required":len(required)-len(missing),"missing":missing,"optional_missing":optional_missing,"ready":not missing}

def manifest(package: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"Item":label,"Required":"Yes" if req else "Optional","Status":"Ready" if package.get(key,{}).get("ready",False) else "Missing","Location":package.get(key,{}).get("location","")} for label,key,req in ITEMS]
