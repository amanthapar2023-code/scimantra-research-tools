"""Rule-based workflow planner for the SciMantra Research OS.

Produces transparent next-action recommendations from project state and audit
signals. It does not execute experiments, publish papers, or make scientific
validity decisions automatically.
"""
from __future__ import annotations
from typing import Any

STAGE_ORDER = [
    "Research Question", "Literature", "Hypothesis", "Experiment", "Data",
    "Analysis", "Evidence", "Claims", "Manuscript", "Peer Review", "Submission", "Next Study",
]


def _action(stage: str, priority: str, title: str, reason: str, suggested_tool: str) -> dict[str, str]:
    return {"stage": stage, "priority": priority, "title": title, "reason": reason, "suggested_tool": suggested_tool}


def plan(project: dict[str, Any], audits: dict[str, Any] | None = None) -> list[dict[str, str]]:
    audits = audits or {}
    stages = project.get("stages", {}) if isinstance(project, dict) else {}
    actions: list[dict[str, str]] = []

    blocked = [s for s in STAGE_ORDER if isinstance(stages.get(s), dict) and stages[s].get("status") == "Blocked"]
    for stage in blocked:
        actions.append(_action(stage, "Critical", f"Unblock {stage}", "This lifecycle stage is explicitly marked blocked in the project.", "Research OS"))

    if stages.get("Research Question", {}).get("status") != "Complete":
        actions.append(_action("Research Question", "High", "Refine the research question", "A defined question anchors the downstream hypothesis and study design.", "Research Question & Hypothesis Forge"))
    if stages.get("Literature", {}).get("status") != "Complete":
        actions.append(_action("Literature", "High", "Build the evidence base", "Literature evidence is needed to establish prior work, methods and gaps.", "Literature Evidence Retriever"))
    if stages.get("Hypothesis", {}).get("status") != "Complete":
        actions.append(_action("Hypothesis", "High", "Create a falsifiable hypothesis", "The experiment should test a clearly stated prediction rather than an undefined expectation.", "Research Question & Hypothesis Forge"))
    if stages.get("Experiment", {}).get("status") != "Complete":
        actions.append(_action("Experiment", "High", "Audit the experimental design", "Controls, comparators, measurements and power should be planned before data collection.", "Research Experiment Architect"))
    if stages.get("Data", {}).get("status") != "Complete":
        actions.append(_action("Data", "Medium", "Register and quality-check the dataset", "Analysis readiness depends on knowing what data exist and where they came from.", "Project Artifact Manager"))
    if stages.get("Analysis", {}).get("status") != "Complete":
        actions.append(_action("Analysis", "High", "Audit analysis assumptions and robustness", "Analysis choices can change the interpretation of the evidence.", "Statistical Assumption Audit / Robustness"))
    if stages.get("Evidence", {}).get("status") != "Complete":
        actions.append(_action("Evidence", "High", "Assess evidence sufficiency", "Claims should be matched to the strength and provenance of their supporting evidence.", "Evidence Sufficiency Engine"))
    if stages.get("Claims", {}).get("status") != "Complete":
        actions.append(_action("Claims", "High", "Stress-test scientific claims", "Check causal scope, certainty, novelty, generalization and quantitative consistency before writing conclusions.", "Research Claim Stress Test"))
    if stages.get("Manuscript", {}).get("status") != "Complete":
        actions.append(_action("Manuscript", "Medium", "Build the evidence-grounded manuscript", "Manuscript statements should remain traceable to project evidence.", "Research Manuscript Studio"))
    if stages.get("Peer Review", {}).get("status") != "Complete":
        actions.append(_action("Peer Review", "Medium", "Run a hostile pre-review", "A pre-submission challenge can expose unresolved design, evidence and reporting weaknesses.", "Hostile Peer Review Simulator"))
    if stages.get("Submission", {}).get("status") != "Complete":
        actions.append(_action("Submission", "Medium", "Run the submission readiness audit", "Submission should follow scientific readiness checks rather than replace them.", "Research Decision Orchestrator"))

    # External audit signals can elevate actions without silently changing stage status.
    if audits.get("broken_links"):
        actions.insert(0, _action("Evidence", "Critical", "Repair broken evidence links", "The cross-tool linkage audit reports broken artifact relationships.", "Cross-Tool Data Linkage"))
    if audits.get("duplicate_ids"):
        actions.insert(0, _action("Evidence", "High", "Resolve duplicate artifact IDs", "Duplicate identifiers weaken provenance and downstream traceability.", "Project Artifact Manager"))
    if audits.get("needs_review"):
        actions.insert(0, _action("Evidence", "High", "Review flagged project artifacts", "One or more project artifacts are explicitly marked as needing review.", "Project Artifact Manager"))

    # Deduplicate by title while preserving priority ordering.
    seen = set(); unique = []
    for item in actions:
        if item["title"] not in seen:
            seen.add(item["title"]); unique.append(item)
    rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(unique, key=lambda x: (rank.get(x["priority"], 9), STAGE_ORDER.index(x["stage"]) if x["stage"] in STAGE_ORDER else 99))


def summary(actions: list[dict[str, str]]) -> dict[str, int]:
    return {
        "total": len(actions),
        "critical": sum(a["priority"] == "Critical" for a in actions),
        "high": sum(a["priority"] == "High" for a in actions),
        "medium": sum(a["priority"] == "Medium" for a in actions),
    }
