import streamlit as st
import pandas as pd
from src.scimantra.literature_retriever import retrieve_and_rank, evidence_ready_record

st.set_page_config(page_title="Literature Evidence Retriever | SciMantra", page_icon="📚", layout="wide")
st.title("📚 Literature Evidence Retriever")
st.caption("Retrieve scholarly metadata, rank title relevance, remove duplicates, and prepare verified papers for your evidence matrix.")

if "literature_results" not in st.session_state:
    st.session_state.literature_results = []

with st.form("literature_retriever"):
    default_query = st.session_state.get("ri_title", "")
    query = st.text_input("Research topic / title", value=default_query, placeholder="Enter a research title, question, or focused topic")
    rows = st.slider("Maximum papers to retrieve", 5, 50, 25)
    search = st.form_submit_button("🔎 Retrieve literature", type="primary")

if search:
    if not query.strip():
        st.warning("Enter a research topic first.")
    else:
        with st.spinner("Retrieving scholarly metadata…"):
            try:
                st.session_state.literature_results = retrieve_and_rank(query.strip(), rows)
                st.session_state.literature_error = ""
            except Exception:
                st.session_state.literature_results = []
                st.session_state.literature_error = "The public literature metadata service could not be reached."

if st.session_state.get("literature_error"):
    st.warning(st.session_state.literature_error)

papers = st.session_state.literature_results
if papers:
    st.metric("Unique literature records", len(papers))
    df = pd.DataFrame(papers)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Export literature metadata", df.to_csv(index=False), "literature_retrieval.csv", "text/csv")

    st.divider()
    st.subheader("🧬 Prepare evidence-matrix seeds")
    st.caption("Select papers you have actually reviewed. Metadata fields are prefilled; scientific evidence fields remain intentionally blank until verified from the source.")
    selected = st.multiselect("Papers to prepare", range(len(papers)), format_func=lambda i: f"{i+1}. {papers[i].get('Title','Untitled')}")
    if selected:
        seeds = [evidence_ready_record(papers[i]) for i in selected]
        st.dataframe(pd.DataFrame(seeds), use_container_width=True, hide_index=True)
        st.download_button("Export evidence-matrix seeds", pd.DataFrame(seeds).to_csv(index=False), "evidence_matrix_seeds.csv", "text/csv")
else:
    st.info("Start with a research title or focused question. Retrieved records will appear here.")

st.info("Integrity rule: this engine retrieves bibliographic metadata only. It does not invent abstracts, findings, research gaps, methods, or conclusions. Verify the full paper before treating any record as evidence.")
