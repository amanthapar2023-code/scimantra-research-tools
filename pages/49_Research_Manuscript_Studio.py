import streamlit as st
import pandas as pd
from src.scimantra.manuscript_studio import SECTIONS, section_template, audit_sections, manuscript_markdown

st.set_page_config(page_title="Research Manuscript Studio | SciMantra", page_icon="📝", layout="wide")
st.title("📝 Research Manuscript Studio")
st.caption("Build a manuscript section-by-section while keeping evidence and source notes visible beside the draft.")

title = st.text_input("Research title", st.session_state.get("ri_title", ""))
if "manuscript_workspace" not in st.session_state:
    st.session_state.manuscript_workspace = section_template(title)

workspace = st.session_state.manuscript_workspace
tab_names = SECTIONS
for section in tab_names:
    with st.expander(section, expanded=(section == "Introduction")):
        item = workspace.setdefault(section, section_template().get(section, {}))
        st.caption(item.get("prompt", ""))
        item["draft"] = st.text_area(f"{section} draft", item.get("draft", ""), height=220, key=f"ms_draft_{section}")
        item["evidence"] = st.text_area("Evidence / source notes", item.get("evidence", ""), height=100, key=f"ms_ev_{section}", placeholder="DOI, page/section, dataset, figure/table, analysis output, or researcher verification note")
        item["status"] = "Evidence linked" if item["draft"].strip() and item["evidence"].strip() else "Draft only" if item["draft"].strip() else "Not started"

st.session_state.manuscript_workspace = workspace
rows = audit_sections(workspace)
st.subheader("Manuscript readiness")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
linked = sum(r["Evidence linked"] for r in rows)
st.metric("Sections with evidence notes", f"{linked}/{len(rows)}")

st.download_button("Download manuscript Markdown", manuscript_markdown(title, workspace), "scimantra_manuscript.md", "text/markdown")
st.warning("This studio organizes and audits writing. It must not be treated as permission to invent results, citations, methods, or unsupported conclusions.")
