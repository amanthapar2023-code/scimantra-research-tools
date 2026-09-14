import streamlit as st
import pandas as pd
from src.scimantra.research_vault import OBJECT_TYPES, STATUSES, new_object, vault_metrics, search_objects, export_vault

st.set_page_config(page_title="Research Knowledge Vault | SciMantra", page_icon="🗃️", layout="wide")
st.title("🗃️ Research Knowledge Vault")
st.caption("Keep the important objects of a research project together, with provenance and status visible.")

if "research_vault" not in st.session_state:
    st.session_state.research_vault = []

project = st.text_input("Project title", value=st.session_state.get("ri_title", ""))
with st.expander("➕ Add research object", expanded=True):
    c1, c2 = st.columns(2)
    kind = c1.selectbox("Object type", OBJECT_TYPES)
    status = c2.selectbox("Status", STATUSES)
    title = st.text_input("Short title")
    content = st.text_area("Research note / evidence / decision", height=120)
    source = st.text_input("Source / provenance", placeholder="DOI, dataset ID, figure/table, protocol file, meeting note…")
    tags = st.text_input("Tags", placeholder="H2S, control, limitation, manuscript")
    if st.button("Save to vault", type="primary"):
        if title.strip():
            st.session_state.research_vault.append(new_object(kind, title, content, source, status, tags))
            st.success("Research object added.")
        else:
            st.warning("Give the object a short title first.")

objects = st.session_state.research_vault
m = vault_metrics(objects)
a,b,c,d = st.columns(4)
a.metric("Research objects", m["objects"])
b.metric("Verified", m["verified"])
c.metric("With provenance", m["sourced"])
d.metric("Source coverage", f"{m['source_coverage']}%")

query = st.text_input("🔎 Search the vault", placeholder="e.g. control, H2S, Figure 2, limitation")
shown = search_objects(objects, query)
if shown:
    st.dataframe(pd.DataFrame(shown), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export knowledge vault", export_vault(objects, project), "scimantra_research_knowledge_vault.md", "text/markdown")
else:
    st.info("No research objects yet. Add questions, papers, evidence, experiments, datasets, results, claims and decisions as the project develops.")

st.divider()
st.subheader("🔗 How this becomes the project memory")
st.write("The vault is designed to become the shared memory layer for Research Intelligence, Evidence Matrix, Methodology, Results, Claim Traceability, Reviewer Attack, Reproducibility, Research Graph and Decision Engine.")
st.warning("This first version stores researcher-entered records in the current app session. It does not silently invent, verify, or alter scientific evidence.")
