from __future__ import annotations

import json
import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st

from src.scimantra.cloud import configured, client, current_user, list_artifacts, list_projects

st.title("🔍 Research Audit & Provenance Explorer")
st.caption("Trace every readiness decision back to the saved artifact, source tool, timestamp, and integrity fingerprint.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to inspect project provenance.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("Create a project in Cloud Research Workspace first.")
    st.stop()

project = projects[[p.get("name") for p in projects].index(st.selectbox("Research project", [p.get("name", "Untitled") for p in projects]))]

try:
    artifacts = list_artifacts(supa, project["id"])
except Exception as exc:
    st.error(f"Could not load project artifacts: {exc}")
    st.stop()


def provenance(a):
    p = a.get("provenance_json", {})
    if isinstance(p, str):
        try: p = json.loads(p)
        except Exception: p = {}
    return p if isinstance(p, dict) else {}


def evidence_text(a):
    return " ".join([str(a.get("name", "")), str(a.get("artifact_type", "")), str(a.get("source_tool", "")), json.dumps(provenance(a), default=str)]).lower()

st.metric("Saved evidence artifacts", len(artifacts))

if not artifacts:
    st.info("No project artifacts are available for audit yet.")
    st.stop()

stage_options = ["All"]
stages = {
    "Dataset": ["dataset", "raw data"],
    "Quality": ["quality audit", "data quality", "quality_gate"],
    "Statistics": ["statistical validation", "replicate-aware"],
    "Evidence": ["evidence passport", "reproducibility evidence", "passport"],
    "Figures": ["publication figure", "figure engine", "figure set"],
    "Manuscript": ["manuscript studio", "complete manuscript", "manuscript"],
    "Submission": ["submission package", "submission packager"],
    "Package": ["research package", "study package", "study packager"],
}
stage_options += list(stages)
selected_stage = st.selectbox("Filter evidence stage", stage_options)

filtered = artifacts
if selected_stage != "All":
    keys = stages[selected_stage]
    filtered = [a for a in artifacts if any(k in evidence_text(a) for k in keys)]

st.subheader("Audit ledger")
rows = []
for a in filtered:
    p = provenance(a)
    rows.append({
        "Artifact": a.get("name", ""),
        "Type": a.get("artifact_type", ""),
        "Source tool": a.get("source_tool", ""),
        "Created": a.get("created_at", ""),
        "Size (bytes)": a.get("size_bytes", 0),
        "SHA-256": a.get("sha256", ""),
        "Provenance fields": len(p),
    })

st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
st.download_button("⬇️ Export audit ledger", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"), "research_audit_ledger.csv", "text/csv")

st.subheader("Artifact-level audit")
for a in filtered:
    title = f"{a.get('name', 'Unnamed')} · {a.get('source_tool') or 'source not recorded'}"
    with st.expander(title):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Artifact type:** {a.get('artifact_type') or 'Not recorded'}")
            st.write(f"**Created:** {a.get('created_at') or 'Not recorded'}")
            st.write(f"**Content type:** {a.get('content_type') or 'Not recorded'}")
            st.write(f"**Size:** {a.get('size_bytes', 0):,} bytes")
        with c2:
            sha = a.get("sha256", "")
            st.write("**SHA-256**")
            st.code(sha or "Not recorded", language=None)
            st.write(f"**Storage path:** {a.get('storage_path') or 'Not recorded'}")
        p = provenance(a)
        st.write("**Saved provenance**")
        if p:
            st.json(p, expanded=True)
        else:
            st.caption("No structured provenance was recorded for this artifact.")

        # Independently hash the stored metadata representation to expose audit identity.
        canonical = json.dumps({k: a.get(k) for k in sorted(a) if k not in {"provenance_json"}}, sort_keys=True, default=str).encode("utf-8")
        st.caption("Metadata audit fingerprint")
        st.code(hashlib.sha256(canonical).hexdigest(), language=None)

st.subheader("Provenance completeness")
complete_fields = ["name", "artifact_type", "source_tool", "storage_path", "sha256", "created_at"]
quality_rows = []
for a in filtered:
    missing = [f for f in complete_fields if not a.get(f)]
    quality_rows.append({"Artifact": a.get("name", ""), "Complete core provenance": not missing, "Missing fields": ", ".join(missing) or "—"})
qdf = pd.DataFrame(quality_rows)
st.dataframe(qdf, width="stretch", hide_index=True)

if not qdf.empty and bool(qdf["Complete core provenance"].all()):
    st.success("All displayed artifacts contain the core provenance fields.")
else:
    st.warning("One or more displayed artifacts have incomplete core provenance. Do not treat an incomplete record as a fully reproducible audit trail.")

st.divider()
st.caption("Integrity safeguard: this explorer audits recorded metadata and provenance. It does not recompute analyses, verify the contents of files, or certify that a scientific conclusion is correct.")
