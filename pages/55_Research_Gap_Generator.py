import streamlit as st
import pandas as pd
from src.scimantra.research_gap import generate_gap_candidates, rank_gap_candidates, gap_validation_checklist, export_gap_candidates

st.set_page_config(page_title="Research Gap Generator | SciMantra", page_icon="🎯", layout="wide")
st.title("🎯 Research Gap Generator")
st.caption("Convert evidence-coverage patterns into testable research-gap hypotheses — then challenge them before writing a novelty claim.")

if "gap_records" not in st.session_state:
    st.session_state.gap_records = []

st.subheader("1. Supply your evidence set")
st.caption("Paste verified evidence from your Evidence Synthesis workflow. This tool deliberately treats gaps as hypotheses requiring verification.")
with st.form("gap_record"):
    title = st.text_input("Paper title")
    source = st.text_input("Source anchor")
    evidence = {}
    fields = ["Problem", "Challenges", "Research solution", "Technology / approach", "Innovation", "Difference from previous work", "Research gap", "Method", "Key result", "Limitation"]
    cols = st.columns(2)
    for i, field in enumerate(fields):
        with cols[i % 2]:
            evidence[field] = st.text_area(field, height=75, key=f"gap_{field}")
    add = st.form_submit_button("➕ Add paper evidence", type="primary")
if add:
    if not title.strip():
        st.warning("Enter a paper title.")
    else:
        st.session_state.gap_records.append({"Title": title.strip(), "Source anchor": source.strip(), **evidence})
        st.success("Paper evidence added.")

records = st.session_state.gap_records
if records:
    st.divider()
    novelty_caution = st.slider("Novelty-collision caution (optional)", 0, 100, 0, help="A caution factor only. It does not determine scientific novelty.")
    raw = generate_gap_candidates(records, st.session_state.get("ri_title", ""))
    rows = rank_gap_candidates(raw, novelty_caution)

    st.subheader("2. Ranked gap hypotheses")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.warning("A high score means incomplete/uneven evidence in the supplied set. It does NOT mean that a scientifically novel gap has been proven.")

    selected = st.selectbox("Gap to challenge", range(len(rows)), format_func=lambda i: f"{rows[i]['Priority']} — {rows[i]['Gap dimension']}")
    row = rows[selected]
    st.subheader("3. Challenge before claiming the gap")
    st.markdown(f"**Candidate question:** {row['Candidate research question']}")
    st.markdown(f"**Possible next study:** {row['Possible next study']}")
    for item in gap_validation_checklist(row):
        st.checkbox(item, key=f"gap_check_{selected}_{item}")

    st.subheader("4. Researcher-defined gap statement")
    statement = st.text_area("Write the final gap only after source verification", placeholder="Based on [specific evidence], it remains unclear whether…")
    if statement.strip():
        st.info("Keep citations and exact evidence locations attached to this statement before transferring it into your manuscript.")

    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export gap hypotheses", export_gap_candidates(rows), "research_gap_candidates.md", "text/markdown")
    if st.button("🗑️ Clear gap workspace"):
        st.session_state.gap_records = []
        st.rerun()
else:
    st.info("Add reviewed paper evidence to generate gap hypotheses.")

st.info("Integrity rule: SciMantra does not declare 'no one has studied this' or certify novelty. Gap hypotheses must be checked against the literature, citations, study context, and original source evidence.")
