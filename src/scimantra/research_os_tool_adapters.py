"""Phase 103: adapters that publish existing SciMantra tool outputs to the OS bus.

Adapters define an explicit contract; they do not silently rewrite or validate
scientific results. A tool can publish an artifact, link it to another artifact,
and record the action on the shared bus.
"""
from __future__ import annotations

from typing import Any

TOOL_REGISTRY = {
    "Research Intelligence": ("research_intelligence", "02 Literature"),
    "Evidence Matrix": ("evidence_matrix", "02 Literature"),
    "Novelty Radar": ("novelty_radar", "02 Literature"),
    "Methodology Designer": ("methodology_designer", "04 Experiment"),
    "Results Interpreter": ("results_interpreter", "06 Analysis"),
    "Publication Figure Engine": ("publication_figures", "06 Analysis"),
    "Claim Traceability": ("claim_traceability", "08 Claims"),
    "Reproducibility Passport": ("reproducibility_passport", "10 Peer Review"),
    "Research Graph": ("research_graph", "08 Claims"),
    "Research Project Copilot": ("research_decision", "12 Next Study"),
    "Manuscript Studio": ("manuscript_studio", "09 Manuscript"),
    "Evidence Writer": ("evidence_writer", "09 Manuscript"),
    "Citation Integrity": ("citation_integrity", "09 Manuscript"),
    "Literature Retriever": ("literature_retriever", "02 Literature"),
    "Evidence Extraction": ("evidence_extraction", "07 Evidence"),
    "Evidence Synthesis": ("evidence_synthesis", "07 Evidence"),
    "Research Gap": ("research_gap", "02 Literature"),
    "Question & Hypothesis Forge": ("question_hypothesis_forge", "03 Hypothesis"),
    "Experiment Architect": ("experiment_architect", "04 Experiment"),
    "Design Optimizer": ("design_optimizer", "04 Experiment"),
    "Falsification Lab": ("falsification_lab", "07 Evidence"),
    "Causal Lab": ("causal_lab", "04 Experiment"),
    "DAG Builder": ("dag_builder", "04 Experiment"),
    "Bias / Error Budget": ("bias_error_budget", "04 Experiment"),
    "Statistical Assumption": ("statistical_assumption", "06 Analysis"),
    "Robustness / Sensitivity": ("robustness_sensitivity", "06 Analysis"),
    "Reproducible Pipeline": ("reproducible_pipeline", "06 Analysis"),
    "Evidence Provenance": ("research_provenance", "07 Evidence"),
    "Research Integrity": ("research_integrity", "08 Claims"),
    "Claim Stress Test": ("claim_stress_test", "08 Claims"),
    "Evidence Sufficiency": ("evidence_sufficiency", "07 Evidence"),
    "Generalizability Auditor": ("generalizability_audit", "08 Claims"),
    "Mechanism Consistency": ("mechanism_consistency", "08 Claims"),
    "Novelty Verification": ("novelty_verification", "02 Literature"),
    "Hostile Peer Review": ("reviewer_simulator", "10 Peer Review"),
    "Decision Orchestrator": ("research_decision_orchestrator", "12 Next Study"),
    "Unified Workspace": ("research_project_workspace", "01 Research Question"),
    "Artifact Manager": ("project_artifact_manager", "01 Research Question"),
    "Workflow Automation": ("research_workflow_automation", "01 Research Question"),
    "Research Copilot 2.0": ("research_copilot", "12 Next Study"),
    "Live Literature": ("live_literature_intelligence", "02 Literature"),
    "Citation Reference Manager": ("citation_reference_manager", "09 Manuscript"),
    "Experiment → Data Bridge": ("experiment_data_bridge", "05 Data"),
    "Automatic Analysis Pipeline": ("automatic_analysis_pipeline", "06 Analysis"),
    "Evidence-Grounded Manuscript": ("evidence_grounded_manuscript", "09 Manuscript"),
    "Claim → Citation Linker": ("claim_citation_linker", "09 Manuscript"),
    "Journal Requirements Auditor": ("journal_requirements_auditor", "10 Peer Review"),
    "Pre-Submission Scientific Audit": ("pre_submission_scientific_audit", "10 Peer Review"),
    "Submission Package Builder": ("submission_package_builder", "11 Submission"),
    "Reviewer Response Manager": ("reviewer_response_manager", "10 Peer Review"),
    "Impact / Reuse Engine": ("research_impact_reuse", "12 Next Study"),
    "Collaboration Workspace": ("collaborative_research_workspace", "01 Research Question"),
    "Persistent Research Store": ("persistent_research_store", "01 Research Question"),
    "Security / Permissions": ("research_security_permissions", "01 Research Question"),
    "Research Audit Trail": ("research_audit_trail", "01 Research Question"),
    "Cross-Project Knowledge": ("cross_project_knowledge", "12 Next Study"),
    "Research Network": ("research_network", "12 Next Study"),
}


def tool_contracts() -> list[dict[str, str]]:
    return [{"tool": name, "module": module, "stage": stage} for name, (module, stage) in TOOL_REGISTRY.items()]


def publish_output(bus: dict[str, Any], source_tool: str, artifact_id: str, title: str, artifact_type: str = "Other", stage: str = "", location: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    from .research_os_data_bus import register_artifact, record_event
    if source_tool not in TOOL_REGISTRY:
        raise ValueError(f"Unknown registered tool: {source_tool}")
    default_stage = TOOL_REGISTRY[source_tool][1]
    bus = register_artifact(bus, artifact_id, title, artifact_type, stage or default_stage, source_tool, location, metadata)
    return record_event(bus, "Researcher", "Published tool output", artifact_id, "artifact", f"Adapter: {source_tool}")


def publish_link(bus: dict[str, Any], source_id: str, target_id: str, link_type: str = "derived_from", note: str = "") -> dict[str, Any]:
    from .research_os_data_bus import link_artifacts, record_event
    bus = link_artifacts(bus, source_id, target_id, link_type, note)
    return record_event(bus, "Researcher", "Linked artifacts", source_id, "artifact", f"{link_type} → {target_id}")


def audit_adapters() -> dict[str, Any]:
    import importlib
    rows = []
    for name, (module, stage) in TOOL_REGISTRY.items():
        try:
            importlib.import_module(f"scimantra.{module}")
            ok, error = True, ""
        except Exception as exc:
            ok, error = False, f"{type(exc).__name__}: {exc}"
        rows.append({"tool": name, "module": module, "stage": stage, "available": ok, "error": error})
    passed = sum(r["available"] for r in rows)
    return {"total": len(rows), "passed": passed, "failed": len(rows) - passed, "coverage_pct": round(100 * passed / len(rows), 1) if rows else 0.0, "rows": rows}


def summary() -> dict[str, int]:
    return {"registered_tools": len(TOOL_REGISTRY), "lifecycle_stages": len(set(stage for _, stage in TOOL_REGISTRY.values()))}
