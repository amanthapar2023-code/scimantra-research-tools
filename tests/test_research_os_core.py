"""Structural reliability tests for the SciMantra Research OS core engines."""
from __future__ import annotations

import json
import pytest

from scimantra.research_os_access import access_status
from scimantra.research_os_data_bus import attach_provenance, audit_bus, link_artifacts, new_bus, register_artifact
from scimantra.research_os_data_contract import audit as contract_audit, envelope, validate
from scimantra.research_os_decision_memory import audit as memory_audit, new_memory, record, search
from scimantra.research_os_next_action import recommend
from scimantra.research_os_output_registry import registry_audit, validate_output
from scimantra.research_os_scientific_audit import actions, readiness, score
from scimantra.research_os_state import add_artifact, from_json, new_project, progress, set_stage, to_json
from scimantra.research_os_sync import ensure_sync_state, mark_dirty, mark_synced, new_sync_state


def test_project_lifecycle_and_roundtrip() -> None:
    project = new_project("Test", "Does X improve Y?")
    project = set_stage(project, "Literature", status="Complete", notes="Reviewed")
    project = add_artifact(project, "Dataset", "Dataset", "Data")
    assert progress(project)["complete"] == 1
    assert progress(project)["total"] == 12
    restored = from_json(to_json(project))
    assert restored["project"]["question"] == "Does X improve Y?"
    assert restored["artifacts"][0]["title"] == "Dataset"


def test_project_rejects_invalid_inputs() -> None:
    project = new_project()
    with pytest.raises(ValueError):
        set_stage(project, "No such stage", status="Complete")
    with pytest.raises(ValueError):
        set_stage(project, "Literature", status="INVALID")
    with pytest.raises(ValueError):
        add_artifact(project, "", "Dataset", "Data")
    with pytest.raises(ValueError):
        from_json("not-json")


def test_data_bus_integrity_and_provenance() -> None:
    bus = new_bus("p1", "Project")
    register_artifact(bus, {"id": "a1", "title": "A", "type": "Dataset"})
    register_artifact(bus, {"id": "a2", "title": "B", "type": "Analysis"})
    link_artifacts(bus, "a1", "a2", "derived_from")
    attach_provenance(bus, "a2", {"source": "test"})
    audit = audit_bus(bus)
    assert audit["healthy"] is True
    assert audit["broken_links"] == []


def test_data_contract_validation_and_duplicate_audit() -> None:
    item = envelope("p1", "a1", "Dataset", "Data", "Test Tool", "Active", {"n": 1})
    assert validate(item) == []
    assert validate({"project_id": "p1"})
    assert contract_audit([item, dict(item)])["duplicates"]


def test_scientific_audit_score_readiness_and_actions() -> None:
    levels = {"Evidence sufficiency": "Strong", "Claim stress test": "Adequate", "Causal validity": "Needs work"}
    result = score(levels)
    assert 0 <= result["score"] <= 100
    assert "classification" in readiness(result)
    assert actions(levels)


def test_decision_memory_search_and_audit() -> None:
    memory = new_memory()
    memory = record(memory, "m1", "Decision", "Use method A", "Rationale", "Successful", tags=["method"])
    memory = record(memory, "m2", "Lesson", "Document controls", "Rationale", "Needs follow-up", tags=["controls"])
    assert len(search(memory, "method")) == 1
    assert memory_audit(memory)["duplicates"] == []


def test_next_action_engine_returns_prioritized_actions() -> None:
    run = {"steps": [{"id": "s1", "name": "Literature", "status": "Not started", "dependencies": []}]}
    result = recommend(run, new_bus("p1", "Project"), [{"level": "critical", "signal": "Missing evidence"}])
    assert result
    assert result[0]["priority"] in {"Critical", "High", "Medium", "Low"}


def test_output_registry_rejects_incomplete_output() -> None:
    valid = {"id": "o1", "title": "Result", "type": "Result", "source_tool": "Test", "stage": "Results"}
    assert validate_output(valid) == []
    assert validate_output({"id": "o1"})
    assert registry_audit([valid, valid])["duplicates"]


def test_access_status_is_safe_without_cloud_secrets() -> None:
    status = access_status({})
    assert status["configured"] is False
    assert "service_key" not in json.dumps(status).lower()


def test_sync_state_transitions_are_deterministic() -> None:
    state = new_sync_state("p1")
    assert state["dirty"] is False
    state = mark_dirty(state)
    assert state["dirty"] is True
    state = mark_synced(state, source="cloud")
    assert state["dirty"] is False
    assert state["source"] == "cloud"
    assert ensure_sync_state({"project_id": "p1"})["project_id"] == "p1"
