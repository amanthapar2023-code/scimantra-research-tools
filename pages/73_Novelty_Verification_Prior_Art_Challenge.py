import pandas as pd
import streamlit as st
from src.scimantra.novelty_verification import template_rows, audit, priority_queue, export_audit, STATUSES

st.set_page_config(page_title="Novelty Verification | SciMantra", page_icon="🔎", layout="wide")
st.title("🔎 Novelty Verification & Prior-Art Challenge")
st.caption("Challenge a proposed contribution against prior work before making a novelty claim.")
st.warning("Integrity rule: this tool does not prove novelty, patentability, or priority. It structures a prior-art challenge and requires verification against the literature and appropriate databases.")

if "novelty_rows" not in st.session_state:
    st.session_state.novelty_rows = template_rows()

left, right = st.columns(2)
with left:
    novelty_claim = st.text_area("Exact novelty claim", height=120, placeholder="What exactly is new in your study?")
with right:
    prior_art = st.text_area("Key prior work / papers to challenge against", height=120, placeholder="Titles, DOIs, citations, patents, datasets, or concise findings")

st.subheader("1. Prior-art dimensions")
for i, row in enumerate(st.session_state.novelty_rows):
    with st.expander(f"{i+1}. {row['Dimension']} — {row['Status']}", expanded=i < 2):
        row["Status"] = st.selectbox("Comparison", STATUSES, index=STATUSES.index(row.get("Status", "Not assessed")), key=f"nv_status_{i}")
        row["Prior work evidence"] = st.text_area("What does prior work actually show?", row.get("Prior work evidence", ""), key=f"nv_prior_{i}")
        row["Proposed contribution"] = st.text_area("What does your work add?", row.get("Proposed contribution", novelty_claim), key=f"nv_new_{i}")
        row["Verification note"] = st.text_input("Verification / citation note", row.get("Verification note", ""), key=f"nv_note_{i}")

if st.button("🔎 Run novelty challenge", type="primary", use_container_width=True):
    st.session_state.novelty_summary = audit(st.session_state.novelty_rows)

summary = st.session_state.get("novelty_summary")
if summary:
    st.divider()
    st.subheader("2. Novelty challenge dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Dimensions assessed", summary["assessed"])
    b.metric("Distinctiveness score", f"{summary['score']}/100")
    c.metric("Distinct", summary["Distinct"])
    d.metric("Highly similar / same", summary["Highly similar"] + summary["Same / already demonstrated"])
    st.dataframe(pd.DataFrame(st.session_state.novelty_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Prior-art risk queue")
    st.dataframe(pd.DataFrame(priority_queue(st.session_state.novelty_rows)), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export novelty challenge", export_audit(st.session_state.novelty_rows, summary), "scimantra_novelty_verification.md", "text/markdown", use_container_width=True)

st.subheader("Reviewer / prior-art questions")
for q in [
    "What is the single smallest unit of novelty: problem, method, system, intervention, outcome, mechanism, application, or combination?",
    "Has the exact combination already been demonstrated even if the individual components are old?",
    "Does the proposed contribution add a measurable capability rather than only a different context?",
    "Is the claimed difference supported by evidence, or is it only a wording difference?",
    "Have adjacent fields and alternative terminology been searched?",
    "Can every novelty statement be linked to a specific prior-art comparison?",
]:
    st.write("• " + q)
