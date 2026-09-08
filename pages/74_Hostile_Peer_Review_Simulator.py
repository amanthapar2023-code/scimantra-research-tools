import pandas as pd
import streamlit as st
from src.scimantra.reviewer_simulator import template, audit, priority_queue, export_review, SEVERITIES

st.set_page_config(page_title="Peer Review Simulator | SciMantra", page_icon="🧑‍⚖️", layout="wide")
st.title("🧑‍⚖️ Hostile Peer-Review Simulator")
st.caption("Try to break the manuscript before Reviewer 2 does.")
st.warning("Integrity rule: these are structured reviewer challenges, not predictions of a journal decision. Resolve them with evidence, analysis, transparent limitations, or manuscript revision.")

if "review_rows" not in st.session_state:
    st.session_state.review_rows = template()

left, right = st.columns(2)
with left:
    title = st.text_input("Manuscript / project title")
    abstract = st.text_area("Abstract or central contribution", height=140, placeholder="Paste the abstract or summarize the study.")
with right:
    methods = st.text_area("Methods / design summary", height=140, placeholder="Design, sample, controls, statistics, main measurements…")

st.subheader("1. Reviewer 2 attack surface")
for i, row in enumerate(st.session_state.review_rows):
    with st.expander(f"{i+1}. {row['Category']} — {row['Severity']}", expanded=i < 2):
        row["Severity"] = st.selectbox("Severity", SEVERITIES, index=SEVERITIES.index(row.get("Severity", "Not assessed")), key=f"rv_sev_{i}")
        st.write("**Reviewer challenge:**", row["Reviewer challenge"])
        row["Evidence / manuscript location"] = st.text_input("Evidence / manuscript location", row.get("Evidence / manuscript location", ""), key=f"rv_ev_{i}")
        row["Author response"] = st.text_area("Author response", row.get("Author response", ""), key=f"rv_resp_{i}")
        row["Revision made"] = st.text_area("Revision / action taken", row.get("Revision made", ""), key=f"rv_rev_{i}")
        row["Resolved"] = st.selectbox("Resolved?", ["No", "Yes", "Partially"], index=["No", "Yes", "Partially"].index(row.get("Resolved", "No")), key=f"rv_res_{i}")

if st.button("🧑‍⚖️ Run reviewer stress-test", type="primary", use_container_width=True):
    st.session_state.review_summary = audit(st.session_state.review_rows)

summary = st.session_state.get("review_summary")
if summary:
    st.divider()
    st.subheader("2. Reviewer risk dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Review points", summary["items"])
    b.metric("Risk index", f"{summary['risk']}/100")
    c.metric("Critical / high", summary["critical"] + summary["high"])
    d.metric("Unresolved", summary["unresolved"])
    st.dataframe(pd.DataFrame(st.session_state.review_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Response priority queue")
    st.dataframe(pd.DataFrame(priority_queue(st.session_state.review_rows)), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export reviewer-response matrix", export_review(st.session_state.review_rows, summary), "scimantra_peer_review_response_matrix.md", "text/markdown", use_container_width=True)

st.subheader("The reviewer mindset")
for q in [
    "What would make me reject the central conclusion?",
    "Which control, replication, or analysis is most important to trust the result?",
    "What alternative explanation has not been eliminated?",
    "Which sentence in the manuscript is stronger than its evidence?",
    "What prior paper could make the novelty claim look incremental?",
    "What information would an independent researcher need to reproduce this result?",
]:
    st.write("• " + q)
