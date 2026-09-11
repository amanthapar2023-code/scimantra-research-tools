from __future__ import annotations
import pandas as pd
import streamlit as st
from src.scimantra.research_os_integration import audit_integration, summary, export_markdown

st.set_page_config(page_title="SciMantra — Integration Audit", page_icon="🧩", layout="wide")
st.title("🧩 Phase 101 — Research OS Integration Audit")
st.caption("Architecture and import-contract audit for the SciMantra Research OS. Scientific validity is not inferred.")

if "os101_report" not in st.session_state:
    st.session_state.os101_report = audit_integration()

if st.button("🔄 Run integration audit", type="primary"):
    st.session_state.os101_report = audit_integration()

report = st.session_state.os101_report
s = summary(report)
c = st.columns(4)
c[0].metric("Checks", s["checks"])
c[1].metric("Passed", s["passed"])
c[2].metric("Failures", s["failures"])
c[3].metric("Coverage", f'{s["coverage_pct"]}%')

if s["failures"] == 0 and s["warnings"] == 0:
    st.success("All registered Phase 101 architecture contracts passed.")
elif s["failures"]:
    st.error(f'{s["failures"]} integration check(s) require repair before end-to-end hardening.')
else:
    st.warning(f'{s["warnings"]} contract check(s) need attention.')

st.divider()
tab1, tab2, tab3 = st.tabs(["🔌 Engine Contracts", "📄 Page Contracts", "🗺️ Integration Map"])
with tab1:
    df = pd.DataFrame(report["engines"])
    view = df[["id","name","stage","importable","status","missing_symbols","error"]].copy()
    st.dataframe(view, width="stretch", hide_index=True)
    bad = df[df["status"] != "PASS"]
    if not bad.empty:
        st.subheader("Repair queue")
        for _, row in bad.iterrows():
            st.warning(f'**{row["name"]}** — {row["status"]}. {row["error"] or ("Missing: " + ", ".join(row["missing_symbols"]))}')
with tab2:
    pages = pd.DataFrame(report["pages"])
    st.dataframe(pages, width="stretch", hide_index=True)
    missing = pages[~pages["exists"]]
    if not missing.empty:
        st.error("Missing registered Research OS pages:")
        st.dataframe(missing[["id","name","path"]], width="stretch", hide_index=True)
with tab3:
    st.markdown("### Research lifecycle wiring target")
    stages = ["Research Question","Literature","Hypothesis","Experiment","Data","Analysis","Evidence","Claims","Manuscript","Peer Review","Submission","Next Study"]
    for i, stage in enumerate(stages, 1):
        st.markdown(f"**{i:02d}. {stage}** → shared project state → artifact registry → provenance/linkage → audit trail → downstream tools")
    st.info("Phase 101 establishes the contract layer. The next hardening passes will replace isolated session-only handoffs with shared project/artifact/linkage state where appropriate.")

st.divider()
st.download_button("⬇️ Export integration audit (Markdown)", export_markdown(report), "scimantra_phase101_integration_audit.md", "text/markdown")
st.caption("⚠️ This audit checks code-level contracts and file availability. It does not verify Supabase credentials, external APIs, authentication enforcement, or complete browser/runtime behavior.")
