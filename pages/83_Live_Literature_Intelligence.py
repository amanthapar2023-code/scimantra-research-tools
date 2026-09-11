"""SciMantra Research OS — live literature intelligence."""
import pandas as pd
import streamlit as st
from src.scimantra.live_literature_intelligence import refresh

st.set_page_config(page_title="Live Literature Intelligence", page_icon="📡", layout="wide")
st.title("📡 Live Literature Intelligence")
st.caption("Refresh scholarly metadata for a research topic and identify newly surfaced papers.")
st.info("This module retrieves public scholarly metadata. It does not infer scientific findings from titles/metadata; verify full text before using a paper as evidence.")

if "live_lit_previous" not in st.session_state: st.session_state.live_lit_previous = []
query = st.text_input("Research topic / literature query", value=st.session_state.get("os_question", ""), placeholder="e.g., volatile organic compounds indoor air quality")
rows = st.slider("Papers to retrieve", 5, 50, 25)
if st.button("🔄 Refresh literature", type="primary", disabled=not query.strip()):
    try:
        result = refresh(query.strip(), rows, st.session_state.live_lit_previous)
        st.session_state.live_lit_result = result
        st.session_state.live_lit_previous = result["papers"]
    except Exception as exc:
        st.error(f"Literature refresh failed: {exc}")

result = st.session_state.get("live_lit_result")
if result:
    a,b,c=st.columns(3); a.metric("Papers surfaced",result["count"]); b.metric("New since previous refresh",result["new_count"]); c.metric("Latest indexed year",result["latest_year"] or "—")
    st.subheader("🆕 Newly surfaced")
    new=result["new_papers"]
    st.dataframe(pd.DataFrame(new)[["Title","Year","Journal","DOI","Relevance"]] if new else pd.DataFrame(columns=["Title","Year","Journal","DOI","Relevance"]),use_container_width=True,hide_index=True)
    st.subheader("📚 Current literature set")
    st.dataframe(pd.DataFrame(result["papers"])[["Title","Year","Authors","Journal","DOI","Relevance","Source"]],use_container_width=True,hide_index=True)
    st.download_button("⬇️ Export literature metadata CSV",pd.DataFrame(result["papers"]).to_csv(index=False),"scimantra_live_literature.csv","text/csv")
else:
    st.subheader("How this module fits the Research OS")
    st.markdown("**Query → Retrieve → Deduplicate → Rank → Compare with previous refresh → Feed candidates into Evidence Matrix / Novelty / Research Gap workflows.**")

st.caption("Module 83 · Live Literature Intelligence · Metadata is not evidence until verified against the source.")
