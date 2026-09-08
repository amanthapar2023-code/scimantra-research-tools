import pandas as pd
import streamlit as st
from src.scimantra.generalizability_audit import template_rows, audit_rows, priority_queue, export_audit, LEVELS

st.set_page_config(page_title="Generalizability Auditor | SciMantra", page_icon="🌍", layout="wide")
st.title("🌍 Generalizability & External Validity Auditor")
st.caption("Test whether a finding can reasonably extend beyond the exact population, system, and conditions studied.")
st.warning("Integrity rule: generalizability is context-dependent. This tool records and prioritizes researcher judgments; it does not prove external validity.")

if "generalizability_rows" not in st.session_state:
    st.session_state.generalizability_rows = template_rows()

c1, c2 = st.columns(2)
with c1:
    claim = st.text_area("Exact claim you want to generalize", placeholder="Paste the manuscript sentence.", height=100)
with c2:
    target = st.text_area("Intended target context", placeholder="Who/what/where/under what conditions should this claim apply?", height=100)

if claim.strip():
    st.info(f"**Claim under audit:** {claim.strip()}\n\n**Target context:** {target.strip() or 'Not specified'}")

st.subheader("1. External-validity domains")
for i, row in enumerate(st.session_state.generalizability_rows):
    with st.expander(f"{i+1}. {row['Domain']} — {row['Status']}", expanded=(i < 2)):
        row["Status"] = st.selectbox("Assessment", LEVELS, index=LEVELS.index(row.get("Status", "Not assessed")), key=f"gv_status_{i}")
        row["Study context"] = st.text_input("What was actually studied?", row.get("Study context", ""), key=f"gv_study_{i}")
        row["Target context"] = st.text_input("What do you want to extend to?", row.get("Target context", target), key=f"gv_target_{i}")
        row["Evidence / notes"] = st.text_area("Evidence / limitation / rationale", row.get("Evidence / notes", ""), key=f"gv_notes_{i}")

if st.button("🌍 Audit external validity", type="primary", use_container_width=True):
    st.session_state.gv_audit = audit_rows(st.session_state.generalizability_rows)

audit = st.session_state.get("gv_audit")
if audit:
    st.divider()
    st.subheader("2. Generalizability dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Assessed domains", audit["assessed"])
    b.metric("Planning score", f"{audit['score']}/100")
    c.metric("Supported", audit["Supported"])
    d.metric("Limited / contradicted", audit["Limited"] + audit["Contradicted"])
    st.dataframe(pd.DataFrame(st.session_state.generalizability_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Highest-priority boundaries")
    st.dataframe(pd.DataFrame(priority_queue(st.session_state.generalizability_rows)), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export external-validity audit", export_audit(st.session_state.generalizability_rows, audit), "scimantra_generalizability_audit.md", "text/markdown", use_container_width=True)
else:
    st.info("Assess the domains and click the audit button to generate the external-validity map.")

st.subheader("Reviewer challenge")
for q in [
    "Exactly which population, system, setting, and conditions were represented by the data?",
    "Which target contexts differ materially from the study context?",
    "Could dose, time, environment, measurement, or selection change the finding?",
    "Is the result replicated across independent samples, batches, operators, or sites?",
    "Should the manuscript explicitly state a boundary instead of implying universal applicability?",
]:
    st.write("• " + q)
