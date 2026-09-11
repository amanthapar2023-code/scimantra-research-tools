from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.scimantra.cloud import configured, client, current_user, list_artifacts, list_projects

st.title("🔗 Research Evidence Graph")
st.caption("Trace the recorded evidence chain from dataset to publication package.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets to use the Evidence Graph.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to view the Evidence Graph.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("Create a project in ☁️ Cloud Project Workspace first.")
    st.stop()

selected = st.selectbox("Research project", [p.get("name", "Untitled") for p in projects])
project = next(p for p in projects if p.get("name") == selected)

try:
    artifacts = list_artifacts(supa, project["id"])
except Exception as exc:
    st.error(f"Could not load project artifacts: {exc}")
    st.stop()


def prov(a):
    p = a.get("provenance_json", {})
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except Exception:
            p = {}
    return p if isinstance(p, dict) else {}


def text(a):
    p = prov(a)
    return " ".join([str(a.get("name", "")), str(a.get("artifact_type", "")), str(a.get("source_tool", "")), json.dumps(p, default=str)]).lower()

stages = [
    ("Dataset", ["dataset", "raw data"]),
    ("Quality", ["quality audit", "data quality", "quality_gate"]),
    ("Statistics", ["statistical validation", "replicate-aware", "statistical"]),
    ("Evidence", ["evidence passport", "reproducibility evidence", "passport"]),
    ("Figures", ["publication figure", "figure engine", "figure set"]),
    ("Manuscript", ["manuscript studio", "complete manuscript", "manuscript"]),
    ("Submission", ["submission package", "submission packager", "submission"]),
    ("Package", ["study package", "research package", "study packager"]),
]

matches = {}
for name, keys in stages:
    matches[name] = [a for a in artifacts if any(k in text(a) for k in keys)]

complete = sum(bool(v) for v in matches.values())
coverage = complete / len(stages) if stages else 0

st.progress(coverage, text=f"Evidence-chain coverage: {complete}/{len(stages)} stages represented")

# Graph-like horizontal chain using native Streamlit columns.
cols = st.columns(len(stages))
for i, (stage, _) in enumerate(stages):
    with cols[i]:
        if matches[stage]:
            st.success("✓")
        else:
            st.warning("○")
        st.markdown(f"**{stage}**")
        st.caption(f"{len(matches[stage])} artifact{'s' if len(matches[stage]) != 1 else ''}")
    if i < len(stages) - 1:
        pass

st.subheader("Evidence links")
for i, (stage, _) in enumerate(stages):
    next_stage = stages[i + 1][0] if i + 1 < len(stages) else None
    found = matches[stage]
    with st.expander(f"{'✅' if found else '⬜'} {stage} — {len(found)} saved artifact(s)", expanded=not bool(found)):
        if found:
            for a in found[:10]:
                p = prov(a)
                st.markdown(f"**{a.get('name', 'Unnamed artifact')}**")
                st.caption(f"Source: {a.get('source_tool') or 'Not recorded'} · Type: {a.get('artifact_type') or 'Not recorded'} · Created: {a.get('created_at') or 'Not recorded'}")
                if a.get("sha256"):
                    st.code(a["sha256"], language=None)
                if p:
                    st.json(p, expanded=False)
        else:
            st.info(f"No saved artifact was detected for **{stage}**.")
            if next_stage:
                st.caption(f"Recommended next link: create/save the {stage} evidence, then continue to {next_stage}.")

st.subheader("Missing links")
missing = [s for s, _ in stages if not matches[s]]
if missing:
    st.warning(" → ".join(missing))
    st.caption("A missing link means no matching saved artifact was found. It does not mean the underlying scientific work was not performed.")
else:
    st.success("Every tracked stage has at least one matching saved artifact.")

st.subheader("Artifact ledger")
if artifacts:
    rows = []
    for a in artifacts:
        rows.append({
            "Stage evidence": next((s for s, _ in stages if a in matches[s]), "Other"),
            "Artifact": a.get("name", ""),
            "Source tool": a.get("source_tool", ""),
            "Type": a.get("artifact_type", ""),
            "Created": a.get("created_at", ""),
            "SHA-256": a.get("sha256", ""),
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.download_button("⬇️ Export Evidence Graph CSV", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"), "research_evidence_graph.csv", "text/csv")
else:
    st.info("The project Vault is empty.")

st.divider()
st.caption("Integrity safeguard: the graph is based only on explicitly saved project artifacts and metadata. It does not infer scientific validity, reproduce analyses, establish causality, or certify journal readiness.")
