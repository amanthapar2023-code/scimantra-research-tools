from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.scimantra.cloud import (
    client,
    configured,
    current_user,
    list_artifacts,
    list_experiments,
    list_milestones,
    list_project_datasets,
    list_projects,
)

st.title("🧭 Research Project Dashboard 2.0")
st.caption("One-screen view of project progress, evidence readiness, and Research Artifact Vault activity.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets to use this dashboard.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to view project dashboards.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("No owned projects found yet. Create a project in ☁️ Cloud Project Workspace.")
    st.stop()

project_names = [p.get("name", "Untitled project") for p in projects]
selected_name = st.selectbox("Research project", project_names)
project = next(p for p in projects if p.get("name") == selected_name)
project_id = project["id"]

try:
    artifacts = list_artifacts(supa, project_id)
    datasets = list_project_datasets(supa, project_id)
    experiments = list_experiments(supa, project_id)
    milestones = list_milestones(supa, project_id)
except Exception as exc:
    st.error(f"Could not load project data: {exc}")
    st.stop()


def provenance(item):
    value = item.get("provenance_json", {})
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {}
    return value if isinstance(value, dict) else {}


def haystack(item):
    p = provenance(item)
    return " ".join(str(x) for x in [item.get("name", ""), item.get("artifact_type", ""), item.get("source_tool", ""), json.dumps(p, default=str)]).lower()

stage_rules = {
    "Dataset": ("dataset", "raw data, registered datasets, or source files"),
    "Quality Audit": ("quality", "data-quality audit or quality-gate evidence"),
    "Statistical Validation": ("stat", "replicate-aware or statistical validation"),
    "Evidence Passport": ("passport", "reproducibility/evidence passport"),
    "Publication Figures": ("figure", "publication-ready figures or figure sets"),
    "Manuscript": ("manuscript", "manuscript/evidence manuscript outputs"),
    "Submission": ("submission", "journal submission package"),
    "Vault": ("vault", "stored project artifacts"),
}

stage_done = {}
for stage, (key, _) in stage_rules.items():
    stage_done[stage] = any(key in haystack(a) for a in artifacts)
stage_done["Dataset"] = bool(datasets) or stage_done["Dataset"]
stage_done["Vault"] = bool(artifacts)

# Broaden matching for the named research pages/tools.
for a in artifacts:
    h = haystack(a)
    if any(x in h for x in ["data quality", "quality audit", "quality_gate"]): stage_done["Quality Audit"] = True
    if any(x in h for x in ["replicate-aware", "statistical validation", "statistical_validation"]): stage_done["Statistical Validation"] = True
    if any(x in h for x in ["evidence passport", "reproducibility evidence", "passport"]): stage_done["Evidence Passport"] = True
    if any(x in h for x in ["publication figure", "figure engine", "figure set"]): stage_done["Publication Figures"] = True
    if any(x in h for x in ["manuscript studio", "complete manuscript", "manuscript"]): stage_done["Manuscript"] = True
    if any(x in h for x in ["submission packager", "submission package", "submission"]): stage_done["Submission"] = True

completed_stages = sum(stage_done.values())
research_stages = list(stage_rules)
progress = completed_stages / len(research_stages) if research_stages else 0

# Readiness values are surfaced only when saved provenance explicitly contains them.
def readiness(kind: str):
    vals = []
    for a in artifacts:
        p = provenance(a)
        keys = [k for k in p if kind in str(k).lower() and ("percent" in str(k).lower() or "readiness" in str(k).lower())]
        for k in keys:
            try:
                v = float(p[k])
                if v <= 1: v *= 100
                if 0 <= v <= 100: vals.append(v)
            except Exception:
                pass
    return max(vals) if vals else None

manuscript_ready = readiness("manuscript")
submission_ready = readiness("submission")

st.progress(progress, text=f"Research pipeline completion: {completed_stages}/{len(research_stages)} stages represented by saved project evidence")

cols = st.columns(6)
metrics = [
    ("Datasets", len(datasets)),
    ("Experiments", len(experiments)),
    ("Milestones", len(milestones)),
    ("Vault artifacts", len(artifacts)),
    ("Evidence stages", f"{completed_stages}/{len(research_stages)}"),
    ("Open milestones", sum(not bool(m.get("completed")) for m in milestones)),
]
for col, (label, value) in zip(cols, metrics):
    col.metric(label, value)

st.subheader("Research pipeline")
st.caption("Completion is inferred from artifacts saved to this project. It is a workflow indicator, not scientific certification.")

stage_cols = st.columns(4)
for i, stage in enumerate(research_stages):
    with stage_cols[i % 4]:
        mark = "✅" if stage_done[stage] else "⬜"
        st.markdown(f"### {mark} {stage}")
        st.caption(stage_rules[stage][1])

left, right = st.columns(2)
with left:
    st.subheader("Readiness")
    st.metric("Manuscript readiness", f"{manuscript_ready:.0f}%" if manuscript_ready is not None else "Not recorded")
    st.metric("Submission readiness", f"{submission_ready:.0f}%" if submission_ready is not None else "Not recorded")
    if manuscript_ready is None or submission_ready is None:
        st.caption("Readiness percentages appear only when explicitly saved in artifact provenance; the dashboard does not invent scores.")

with right:
    st.subheader("Next recommended action")
    next_stage = next((s for s in research_stages if not stage_done[s]), None)
    if next_stage:
        st.info(f"**{next_stage}** is the next represented stage. Create/save the corresponding evidence artifact in the relevant SciMantra tool.")
    else:
        st.success("All tracked research stages are represented in the project Vault. Review the evidence chain before submission.")
    open_milestones = [m for m in milestones if not m.get("completed")]
    if open_milestones:
        st.caption("Open milestone: " + str(open_milestones[0].get("title", "Untitled")))

st.subheader("Recent project activity")
if artifacts:
    rows = []
    for a in artifacts[:10]:
        p = provenance(a)
        rows.append({
            "Artifact": a.get("name", ""),
            "Type": a.get("artifact_type", ""),
            "Source tool": a.get("source_tool", ""),
            "Created": a.get("created_at", ""),
            "SHA-256": a.get("sha256", "")[:12] + ("…" if a.get("sha256") else ""),
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
else:
    st.info("No Vault artifacts have been saved for this project yet.")

with st.expander("Project details"):
    st.write(f"**Project:** {project.get('name', '')}")
    st.write(f"**Status:** {project.get('status', '')}")
    st.write(f"**Objective:** {project.get('objective', '') or 'Not specified'}")
    st.write(f"**Last updated:** {project.get('updated_at', '') or 'Not recorded'}")

st.divider()
st.caption("Scientific safeguard: this dashboard summarizes recorded workflow evidence. It does not validate experimental design, statistical assumptions, causality, or publication eligibility.")
