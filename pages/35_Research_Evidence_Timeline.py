from __future__ import annotations

from datetime import datetime
import pandas as pd
import streamlit as st
from src.scimantra.cloud import client, configured, list_artifacts

st.title("🧭 Research Evidence Timeline")
st.caption("A chronological view of the evidence generated for the active research project.")

try:
    supa = client(st.secrets) if configured(st.secrets) else None
    user = supa.auth.get_user().user if supa else None
except Exception:
    supa = None
    user = None

if not supa or not user:
    st.info("Sign in to SciMantra Cloud to view the persistent research timeline.")
    st.stop()

projects = supa.table("projects").select("id,name,updated_at").order("updated_at", desc=True).execute().data or []
if not projects:
    st.warning("Create a research project in Cloud Project Workspace first.")
    st.stop()

project_map = {p["name"]: p for p in projects}
project_name = st.selectbox("Research project", list(project_map), key="timeline_project")
project_id = project_map[project_name]["id"]
artifacts = list_artifacts(supa, project_id)

# Normalize artifact metadata into a timeline-friendly table.
rows = []
for a in artifacts:
    prov = a.get("provenance_json") or {}
    created = a.get("created_at") or prov.get("uploaded_at")
    rows.append({
        "Created": created or "",
        "Artifact": a.get("name", ""),
        "Stage": a.get("artifact_type", "other").replace("_", " ").title(),
        "Source tool": a.get("source_tool") or "Manual upload",
        "Size (KB)": round((a.get("size_bytes") or 0) / 1024, 1),
        "SHA-256": a.get("sha256", ""),
        "Storage": a.get("storage_path", ""),
        "Provenance": prov.get("note", ""),
    })

df = pd.DataFrame(rows)
if df.empty:
    st.info("No artifacts have been saved to this project yet.")
    st.stop()

df["_dt"] = pd.to_datetime(df["Created"], errors="coerce", utc=True)
df = df.sort_values("_dt", ascending=False)

c = st.columns(4)
c[0].metric("Evidence artifacts", len(df))
c[1].metric("Research stages", df["Stage"].nunique())
c[2].metric("Source tools", df["Source tool"].nunique())
c[3].metric("Latest", df["_dt"].max().strftime("%d %b %Y") if df["_dt"].notna().any() else "—")

st.subheader("🔬 Evidence chain")
st.caption("The timeline reflects saved project artifacts. It does not infer missing experimental steps or certify scientific validity.")

stage_order = ["Dataset", "Analysis", "Evidence", "Figure", "Report", "Manuscript", "Submission", "Package", "Other"]
for stage in stage_order:
    part = df[df["Stage"] == stage]
    if part.empty:
        continue
    st.markdown(f"### {stage}")
    for _, r in part.iterrows():
        with st.container(border=True):
            left, mid, right = st.columns([2.5, 1.3, 1.2])
            left.markdown(f"**{r['Artifact']}**")
            left.caption(f"{r['Source tool']} • {r['Provenance'] or 'No provenance note'}")
            mid.write(r["_dt"].strftime("%d %b %Y, %H:%M UTC") if pd.notna(r["_dt"]) else "Date unavailable")
            right.write(f"{r['Size (KB)']:.1f} KB")
            if r["SHA-256"]:
                st.code(r["SHA-256"], language=None)

with st.expander("📋 Full artifact ledger"):
    st.dataframe(df.drop(columns=["_dt", "Storage"]), width="stretch", hide_index=True)
    csv = df.drop(columns=["_dt"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export evidence ledger CSV", csv, "research_evidence_timeline.csv", "text/csv", width="stretch")

st.success("Evidence timeline loaded from the project's persistent Artifact Vault.")
st.info("Research integrity safeguard: timestamps, fingerprints and provenance are displayed as recorded. They are not a substitute for raw laboratory records, preregistration, institutional records or independent verification.")
