import streamlit as st
import pandas as pd
from src.scimantra.research_memory import CATEGORIES, memory_item, add_memory, search_memory, memory_stats, export_memory

st.set_page_config(page_title="Research Memory Vault | SciMantra", page_icon="🧠", layout="wide")
st.title("🧠 Research Memory Vault")
st.caption("Keep the important history of a research project in one structured, searchable place.")

if "research_memory" not in st.session_state:
    st.session_state.research_memory = []

with st.form("memory_form"):
    category = st.selectbox("Memory type", CATEGORIES)
    title = st.text_input("Title / short label")
    content = st.text_area("What should SciMantra remember?", height=130)
    source = st.text_input("Source / DOI / dataset / notebook / file reference (optional)")
    status = st.selectbox("Status", ["Active", "Resolved", "Needs verification", "Archived"])
    submitted = st.form_submit_button("➕ Save to project memory", type="primary")
    if submitted:
        if title.strip() and content.strip():
            st.session_state.research_memory = add_memory(st.session_state.research_memory, memory_item(category, title, content, source, status))
            st.success("Saved to research memory.")
        else:
            st.error("Add both a title and content before saving.")

memory = st.session_state.research_memory
stats = memory_stats(memory)
cols = st.columns(5)
cols[0].metric("Total entries", len(memory))
cols[1].metric("Literature", stats["Literature"])
cols[2].metric("Experiments", stats["Experiment"])
cols[3].metric("Evidence", stats["Evidence"])
cols[4].metric("Failures", stats["Failure"])

st.divider()
query = st.text_input("🔎 Search project memory")
filtered = search_memory(memory, query)
if filtered:
    st.dataframe(pd.DataFrame(filtered), width="stretch", hide_index=True)
    st.download_button("Download memory as Markdown", export_memory(filtered), "scimantra_research_memory.md", "text/markdown")
else:
    st.info("No memory entries yet. Record literature insights, decisions, experiments, failed approaches, evidence, claims and tasks as the project evolves.")

st.info("Integrity rule: the vault stores researcher-provided information. It does not silently invent, verify, or rewrite scientific history.")
