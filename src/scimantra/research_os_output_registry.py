"""Phase 104: structured output registration for the SciMantra Research OS.

This layer standardizes how specialist tools describe outputs before those outputs
enter the shared OS bus. Registration is metadata plumbing; it does not infer
scientific validity, authorship, causality, novelty, or evidence support.
"""
from __future__ import annotations

from typing import Any

OUTPUT_TYPES = [
    "Question", "Literature", "Evidence", "Hypothesis", "Protocol", "Dataset",
    "Analysis", "Result", "Figure", "Table", "Claim", "Manuscript", "Review", "Other",
]

REQUIRED = ["id", "title", "type", "source_tool", "stage"]


def output_record(
    artifact_id: str,
    title: str,
    artifact_type: str,
    source_tool: str,
    stage: str,
    location: str = "",
    description: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a normalized researcher-selected output descriptor."""
    record = {
        "id": str(artifact_id).strip(),
        "title": str(title).strip(),
        "type": str(artifact_type).strip() or "Other",
        "source_tool": str(source_tool).strip(),
        "stage": str(stage).strip(),
        "location": str(location).strip(),
        "description": str(description).strip(),
        "metadata": metadata if isinstance(metadata, dict) else {},
    }
    return record


def validate_output(record: dict[str, Any]) -> list[str]:
    """Return structural issues; an empty list means structurally ready."""
    issues = []
    for field in REQUIRED:
        if not str(record.get(field, "")).strip():
            issues.append(f"Missing {field}")
    if record.get("type") not in OUTPUT_TYPES:
        issues.append("Unknown output type")
    return issues


def register_output(bus: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Validate and publish one output through the canonical Research OS bus."""
    from .research_os_data_bus import register_artifact, record_event
    from .research_os_tool_adapters import TOOL_REGISTRY

    issues = validate_output(record)
    if issues:
        raise ValueError("; ".join(issues))
    if record["source_tool"] not in TOOL_REGISTRY:
        raise ValueError(f"Unknown registered tool: {record['source_tool']}")
    bus = register_artifact(
        bus,
        record["id"],
        record["title"],
        record["type"],
        record["stage"],
        record["source_tool"],
        record.get("location", ""),
        {"description": record.get("description", ""), **record.get("metadata", {})},
    )
    return record_event(
        bus,
        "Researcher",
        "Registered tool output",
        record["id"],
        "artifact",
        f"Output registry: {record['source_tool']}",
    )


def register_outputs(bus: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    """Publish a batch atomically from the caller's perspective."""
    normalized = [output_record(**r) if "id" in r else r for r in records]
    errors = []
    for i, record in enumerate(normalized, 1):
        issues = validate_output(record)
        if issues:
            errors.append(f"Output {i}: " + ", ".join(issues))
    if errors:
        raise ValueError(" | ".join(errors))
    out = bus
    for record in normalized:
        out = register_output(out, record)
    return out


def registry_audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [str(r.get("id", "")).strip() for r in records]
    duplicates = sorted({x for x in ids if x and ids.count(x) > 1})
    rows = []
    for record in records:
        issues = validate_output(record)
        rows.append({"id": record.get("id", ""), "title": record.get("title", ""), "source_tool": record.get("source_tool", ""), "ready": not issues, "issues": "; ".join(issues)})
    ready = sum(row["ready"] for row in rows)
    return {
        "total": len(rows),
        "ready": ready,
        "needs_review": len(rows) - ready,
        "duplicates": duplicates,
        "rows": rows,
        "healthy": not duplicates and ready == len(rows),
    }


def summary(records: list[dict[str, Any]]) -> dict[str, int]:
    audit = registry_audit(records)
    return {"outputs": audit["total"], "ready": audit["ready"], "needs_review": audit["needs_review"], "duplicates": len(audit["duplicates"])}
