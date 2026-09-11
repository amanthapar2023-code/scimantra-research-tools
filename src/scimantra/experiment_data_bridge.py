"""Experiment-to-data bridge for the SciMantra Research OS."""
from __future__ import annotations
from typing import Any

FIELDS = ["id", "experiment_id", "dataset_id", "protocol_id", "condition", "sample_count", "measurement", "unit", "replicate", "notes"]

def new_record(experiment_id: str, dataset_id: str, protocol_id: str = "") -> dict[str, Any]:
    return {"id": "", "experiment_id": experiment_id, "dataset_id": dataset_id, "protocol_id": protocol_id, "condition": "", "sample_count": "", "measurement": "", "unit": "", "replicate": "", "notes": ""}

def validate(records: list[dict[str, Any]]) -> dict[str, Any]:
    missing = []
    for i, r in enumerate(records, 1):
        required = ["id", "experiment_id", "dataset_id", "condition"]
        absent = [x for x in required if not str(r.get(x, "")).strip()]
        if absent: missing.append({"row": i, "missing": absent})
    ids = [str(r.get("id", "")).strip() for r in records if str(r.get("id", "")).strip()]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    return {"records": len(records), "missing_required": missing, "duplicate_ids": duplicates, "ready": not missing and not duplicates}

def link(experiment: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    return {"experiment_id": experiment.get("id", ""), "experiment_title": experiment.get("title", ""), "dataset_id": dataset.get("id", ""), "dataset_title": dataset.get("title", ""), "relationship": "experiment_generated_dataset"}
