"""Phase 101 integration audit for the SciMantra Research OS.

Checks that the Research OS building blocks exist, import cleanly, expose their
expected contracts, and have corresponding Streamlit pages. This is an
architecture/runtime-readiness audit; it does not execute scientific methods.
"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

CONTRACTS: list[dict[str, Any]] = [
    {"id":"state","name":"Research OS State","module":"src.scimantra.research_os_state","symbols":["new_project","normalize_project","set_stage","add_artifact","progress","to_json","from_json"],"stage":"All"},
    {"id":"linkage","name":"Cross-Tool Linkage","module":"src.scimantra.cross_tool_linkage","symbols":["register_artifact","link_artifacts","trace","audit_bus"],"stage":"All"},
    {"id":"artifacts","name":"Project Artifact Manager","module":"src.scimantra.project_artifact_manager","symbols":["ensure_manager","add_artifact","update_status","audit_artifacts","summary"],"stage":"All"},
    {"id":"provenance","name":"Evidence Provenance Vault","module":"src.scimantra.research_provenance","symbols":["template","audit","provenance_queue","trace_sentence","export_vault"],"stage":"Evidence"},
    {"id":"integrity","name":"Research Integrity Engine","module":"src.scimantra.research_integrity","symbols":["audit"],"stage":"Claims"},
    {"id":"automation","name":"Workflow Automation","module":"src.scimantra.research_workflow_automation","symbols":["new_workflow","audit","next_actions"],"stage":"All"},
    {"id":"copilot","name":"Research Copilot 2.0","module":"src.scimantra.research_copilot","symbols":["answer"],"stage":"All"},
    {"id":"literature","name":"Live Literature Intelligence","module":"src.scimantra.live_literature_intelligence","symbols":["search_plan","audit"],"stage":"Literature"},
    {"id":"citations","name":"Citation Reference Manager","module":"src.scimantra.citation_reference_manager","symbols":["new_library","add_reference","audit"],"stage":"Literature"},
    {"id":"experiment_data","name":"Experiment → Data Bridge","module":"src.scimantra.experiment_data_bridge","symbols":["new_record","validate","link"],"stage":"Experiment"},
    {"id":"analysis","name":"Automatic Analysis Pipeline","module":"src.scimantra.automatic_analysis_pipeline","symbols":["new_pipeline","audit","next_actions"],"stage":"Analysis"},
    {"id":"manuscript","name":"Evidence-Grounded Manuscript","module":"src.scimantra.evidence_grounded_manuscript","symbols":["draft_section","audit_draft"],"stage":"Manuscript"},
    {"id":"claim_citation","name":"Claim → Citation Linker","module":"src.scimantra.claim_citation_linker","symbols":["new_claim","link_citation","audit"],"stage":"Claims"},
    {"id":"journal","name":"Journal Requirements Auditor","module":"src.scimantra.journal_requirements_auditor","symbols":["audit","next_actions"],"stage":"Submission"},
    {"id":"pre_submission","name":"Pre-Submission Scientific Audit","module":"src.scimantra.pre_submission_scientific_audit","symbols":["audit","actions"],"stage":"Submission"},
    {"id":"submission","name":"Submission Package Builder","module":"src.scimantra.submission_package_builder","symbols":["audit","manifest"],"stage":"Submission"},
    {"id":"review","name":"Reviewer Response Manager","module":"src.scimantra.reviewer_response_manager","symbols":["audit","priority_queue","response_template"],"stage":"Peer Review"},
    {"id":"workspace","name":"Unified Research Workspace","module":"src.scimantra.research_project_workspace","symbols":["template","audit","next_steps"],"stage":"All"},
    {"id":"cloud","name":"Persistent Research Store","module":"src.scimantra.persistent_research_store","symbols":["new_store","add_entity","audit_store","export_json"],"stage":"All"},
    {"id":"security","name":"Security & Permissions","module":"src.scimantra.research_security_permissions","symbols":["can","audit_members"],"stage":"All"},
    {"id":"audit_trail","name":"Research Audit Trail","module":"src.scimantra.research_audit_trail","symbols":["event","append","audit","history"],"stage":"All"},
    {"id":"knowledge","name":"Cross-Project Knowledge","module":"src.scimantra.cross_project_knowledge","symbols":["new_index","add_record","search","reusable"],"stage":"Next Study"},
    {"id":"network","name":"Research Network","module":"src.scimantra.research_network","symbols":[],"stage":"All"},
]

PAGE_CONTRACTS = [
    ("78","pages/78_SciMantra_Research_OS.py","Research OS Command Center"),
    ("80","pages/80_Project_Artifact_Manager.py","Project Artifact Manager"),
    ("81","pages/81_Research_Workflow_Automation.py","Workflow Automation"),
    ("82","pages/82_Research_Copilot_2.py","Research Copilot 2.0"),
    ("83","pages/83_Live_Literature_Intelligence.py","Live Literature Intelligence"),
    ("84","pages/84_Citation_Reference_Manager.py","Citation Reference Manager"),
    ("85","pages/85_Experiment_Data_Integration.py","Experiment → Data"),
    ("86","pages/86_Automatic_Analysis_Pipeline.py","Automatic Analysis"),
    ("87","pages/87_Evidence_Grounded_Manuscript_Generator.py","Evidence-Grounded Manuscript"),
    ("88","pages/88_Claim_to_Citation_Auto_Linking.py","Claim → Citation"),
    ("89","pages/89_Journal_Reviewer_Requirements_Auditor.py","Journal Requirements"),
    ("90","pages/90_Pre_Submission_Scientific_Audit.py","Pre-Submission Audit"),
    ("91","pages/91_Submission_Package_Builder.py","Submission Package"),
    ("92","pages/92_Reviewer_Response_Manager.py","Reviewer Response"),
    ("93","pages/93_Research_Impact_Reuse_Engine.py","Impact & Reuse"),
    ("94","pages/94_Collaborative_Research_Workspace.py","Collaboration"),
    ("95","pages/95_Persistent_Research_Database.py","Persistent Store"),
    ("96","pages/96_Research_Security_Permissions.py","Security"),
    ("97","pages/97_Research_Audit_Trail.py","Audit Trail"),
    ("98","pages/98_Cross_Project_Knowledge_Engine.py","Knowledge Engine"),
    ("99","pages/99_SciMantra_Research_Network.py","Research Network"),
    ("100","pages/100_SciMantra_Research_OS_Completion.py","OS Completion"),
]


def _check_contract(item: dict[str, Any]) -> dict[str, Any]:
    module_name = item["module"]
    try:
        mod = import_module(module_name)
        missing = [name for name in item["symbols"] if not hasattr(mod, name)]
        return {"id":item["id"],"name":item["name"],"module":module_name,"stage":item["stage"],"exists":True,"importable":True,"missing_symbols":missing,"status":"PASS" if not missing else "WARN","error":""}
    except Exception as exc:
        return {"id":item["id"],"name":item["name"],"module":module_name,"stage":item["stage"],"exists":False,"importable":False,"missing_symbols":item["symbols"],"status":"FAIL","error":f"{type(exc).__name__}: {exc}"}


def audit_integration() -> dict[str, Any]:
    engine_rows = [_check_contract(item) for item in CONTRACTS]
    page_rows = []
    for ident, path, name in PAGE_CONTRACTS:
        exists = (ROOT / path).exists()
        page_rows.append({"id":ident,"name":name,"path":path,"exists":exists,"status":"PASS" if exists else "FAIL"})
    failures = [r for r in engine_rows if r["status"] == "FAIL"] + [r for r in page_rows if r["status"] == "FAIL"]
    warnings = [r for r in engine_rows if r["status"] == "WARN"]
    return {"engines":engine_rows,"pages":page_rows,"engine_count":len(engine_rows),"page_count":len(page_rows),"failures":len(failures),"warnings":len(warnings),"healthy":not failures and not warnings}


def summary(report: dict[str, Any]) -> dict[str, Any]:
    passed_engines = sum(r["status"] == "PASS" for r in report["engines"])
    passed_pages = sum(r["status"] == "PASS" for r in report["pages"])
    total = report["engine_count"] + report["page_count"]
    passed = passed_engines + passed_pages
    return {"checks":total,"passed":passed,"failures":report["failures"],"warnings":report["warnings"],"coverage_pct":round(100*passed/total,1) if total else 0.0}


def export_markdown(report: dict[str, Any]) -> str:
    s=summary(report)
    lines=["# SciMantra Research OS — Phase 101 Integration Audit","",f"**Coverage:** {s['coverage_pct']}% ({s['passed']}/{s['checks']})","", "## Engine contracts", "", "| Component | Stage | Import | Contract | Error |", "|---|---|---|---|---|"]
    for r in report["engines"]:
        contract="OK" if not r["missing_symbols"] else "Missing: "+", ".join(r["missing_symbols"])
        lines.append(f"| {r['name']} | {r['stage']} | {r['status']} | {contract} | {r['error']} |")
    lines += ["", "## Page contracts", "", "| Module | Page | Status |", "|---|---|---|"]
    for r in report["pages"]: lines.append(f"| {r['id']} — {r['name']} | `{r['path']}` | {r['status']} |")
    lines += ["", "## Interpretation", "", "This audit verifies architecture-level availability and Python import contracts. It does not certify scientific correctness, external-service configuration, authentication enforcement, or end-to-end Streamlit behavior."]
    return "\n".join(lines)
