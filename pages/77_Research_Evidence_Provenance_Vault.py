import pandas as pd
import streamlit as st
from src.scimantra.research_provenance import template, audit, provenance_queue, trace_sentence, export_vault, TYPES, STATUSES

st.set_page_config(page_title="Evidence Provenance Vault | SciMantra", page_icon="🔗", layout="wide")
st.title("🔗 Research Evidence Provenance Vault")
st.caption("Build an auditable chain from manuscript sentence back to raw evidence.")
st.warning("Integrity rule: this vault records researcher-supplied provenance. It does not certify data authenticity, source accuracy, or scientific correctness.")

if "prov_rows" not in st.session_state:
    st.session_state.prov_rows = template()

st.subheader("1. Provenance ledger")
for i, row in enumerate(st.session_state.prov_rows):
    with st.expander(f"{row['ID']} · {row['Type']}", expanded=i < 2):
        c1,c2 = st.columns(2)
        row["Type"] = c1.selectbox("Record type", TYPES, index=TYPES.index(row["Type"]), key=f"p_type_{i}")
        row["Status"] = c2.selectbox("Verification status", STATUSES, index=STATUSES.index(row["Status"]), key=f"p_status_{i}")
        row["Title / statement"] = st.text_input("Dataset / result / claim / sentence", row["Title / statement"], key=f"p_title_{i}")
        c1,c2 = st.columns(2)
        row["Parent ID"] = c1.text_input("Parent record ID", row["Parent ID"], key=f"p_parent_{i}", placeholder="e.g. P003")
        row["Source / location"] = c2.text_input("Source / file / table / page / location", row["Source / location"], key=f"p_source_{i}")
        row["Notes"] = st.text_area("Notes", row["Notes"], key=f"p_notes_{i}")

if st.button("🔍 Audit provenance chain", type="primary", use_container_width=True):
    st.session_state.prov_summary = audit(st.session_state.prov_rows)

summary = st.session_state.get("prov_summary")
if summary:
    st.divider(); st.subheader("2. Provenance dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Records", summary["records"]); b.metric("Verified", summary["verified"]); c.metric("Unresolved", summary["unresolved"]); d.metric("Coverage", f"{summary['coverage']}%")
    if summary["duplicate_ids"]: st.error("Duplicate IDs: " + ", ".join(summary["duplicate_ids"]))
    if summary["broken_links"]: st.error("Broken parent links: " + ", ".join(summary["broken_links"]))
    if summary["missing_parent"]: st.warning("Records missing parent links: " + ", ".join(summary["missing_parent"]))
    st.dataframe(pd.DataFrame(st.session_state.prov_rows), use_container_width=True, hide_index=True)

    st.subheader("3. Provenance priority queue")
    st.dataframe(pd.DataFrame(provenance_queue(st.session_state.prov_rows)), use_container_width=True, hide_index=True)

    sentence_id = st.text_input("Trace a manuscript sentence record by ID", placeholder="e.g. P008")
    if sentence_id:
        chain = trace_sentence(sentence_id.strip(), st.session_state.prov_rows)
        if chain:
            st.write(" → ".join(r["ID"] for r in chain))
            st.dataframe(pd.DataFrame(chain), use_container_width=True, hide_index=True)
        else: st.info("No matching record found.")

    st.download_button("⬇️ Export provenance vault", export_vault(st.session_state.prov_rows, summary), "scimantra_evidence_provenance_vault.md", "text/markdown", use_container_width=True)

st.subheader("Core question")
st.write("**For every important sentence: what claim does it express, which result supports it, which analysis produced that result, and where did the underlying evidence originate?**")
