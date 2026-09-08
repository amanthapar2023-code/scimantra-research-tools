import streamlit as st
import pandas as pd
from src.scimantra.evidence_synthesis import (
    FIELDS, field_coverage, contradiction_signals, gap_map,
    theme_frequency, synthesis_summary, export_synthesis,
)

st.set_page_config(page_title="Evidence Synthesis & Gap Engine | SciMantra", page_icon="🧠", layout="wide")
st.title("🧠 Evidence Synthesis & Gap Engine")
st.caption("Compare verified evidence across papers and surface reviewable gap signals — without pretending that lexical patterns prove a scientific gap.")

if "synthesis_records" not in st.session_state:
    st.session_state.synthesis_records = []

st.subheader("1. Build the comparison set")
st.caption("Paste evidence you have extracted and verified from each paper. Empty fields remain missing evidence.")

with st.form("add_synthesis_paper"):
    title = st.text_input("Paper title", placeholder="Paper 1")
    source = st.text_input("Source anchor", placeholder="DOI / citation key")
    cols = st.columns(2)
    values = {}
    for i, field in enumerate(FIELDS):
        with cols[i % 2]:
            values[field] = st.text_area(field, height=90, key=f"syn_{field}")
    add = st.form_submit_button("➕ Add verified paper", type="primary")

if add:
    if not title.strip():
        st.warning("Enter a paper title.")
    else:
        record = {"Title": title.strip(), "Source anchor": source.strip(), **values}
        st.session_state.synthesis_records.append(record)
        st.success(f"Added: {title.strip()}")

records = st.session_state.synthesis_records
if records:
    st.divider()
    summary = synthesis_summary(records)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Papers", summary["Papers"])
    c2.metric("Average evidence coverage", f"{summary['Average evidence coverage %']}%")
    c3.metric("Strongest dimension", summary["Strongest dimension"])
    c4.metric("Weakest dimension", summary["Weakest dimension"])

    st.subheader("2. Evidence coverage map")
    coverage = field_coverage(records)
    st.dataframe(pd.DataFrame(coverage), use_container_width=True, hide_index=True)

    st.subheader("3. Research-gap signals")
    gaps = gap_map(records)
    st.dataframe(pd.DataFrame(gaps), use_container_width=True, hide_index=True)
    st.warning("A missing field is an evidence-coverage problem, not proof that the literature has no work on that topic. Verify every proposed gap against the original papers.")

    st.subheader("4. Cross-paper divergence review")
    divergence = contradiction_signals(records)
    if divergence:
        st.dataframe(pd.DataFrame(divergence), use_container_width=True, hide_index=True)
        st.caption("Low lexical overlap is only a prompt to inspect papers for genuinely different findings, methods, populations, or contexts. It is not a contradiction detector.")

    st.subheader("5. Recurring technology / approach themes")
    themes = theme_frequency(records)
    if themes:
        st.dataframe(pd.DataFrame(themes), use_container_width=True, hide_index=True)
    else:
        st.info("Add Technology / approach evidence to reveal recurring terms.")

    st.subheader("6. Evidence comparison table")
    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)

    md = export_synthesis(summary, coverage, gaps, divergence)
    st.download_button("⬇️ Export synthesis report", md, "evidence_synthesis_gap_report.md", "text/markdown")
    if st.button("🗑️ Clear comparison set"):
        st.session_state.synthesis_records = []
        st.rerun()
else:
    st.info("Add at least two reviewed papers to make cross-paper comparison meaningful.")

st.info("Integrity rule: this engine synthesizes only researcher-supplied evidence. It does not fabricate findings, declare novelty, or automatically prove a research gap. Every gap signal must be checked against the source literature.")
