import streamlit as st
import pandas as pd
from src.scimantra.evidence_writer import TYPES, draft_frame, audit_sentence, export_entries

st.set_page_config(page_title="Evidence-Grounded Writing | SciMantra", page_icon="🛡️", layout="wide")
st.title("🛡️ Evidence-Grounded Writing")
st.caption("Create manuscript-ready sentence frames only when the researcher supplies the underlying evidence.")

if "evidence_writing_entries" not in st.session_state:
    st.session_state.evidence_writing_entries = []

with st.form("evidence_writer"):
    claim_type = st.selectbox("Writing purpose", TYPES)
    statement = st.text_area("Research statement / finding", height=120, placeholder="Write the statement you want to communicate.")
    evidence = st.text_area("Evidence or source anchor", height=120, placeholder="DOI, paper section/page, dataset, table/figure, analysis output, or researcher-verified note")
    go = st.form_submit_button("Generate evidence-grounded frame", type="primary")

if go:
    result = draft_frame(claim_type, statement, evidence)
    if result["status"] == "Evidence supplied":
        result.update({"type": claim_type})
        st.session_state.evidence_writing_entries.append(result)
        st.success("Draft frame created. Verify wording against the source before manuscript use.")
    else:
        st.warning(result["status"])

if st.session_state.evidence_writing_entries:
    st.subheader("Draft queue")
    for i, entry in enumerate(st.session_state.evidence_writing_entries, 1):
        st.markdown(f"**{i}. {entry['type']}**")
        st.write(entry["text"])
        st.caption("Evidence: " + entry.get("evidence", ""))
        audit = audit_sentence(entry["text"], entry.get("evidence", ""))
        if audit["Potential causal wording"]:
            st.warning("Potential causal wording detected — confirm that the study design supports a causal claim.")
    st.dataframe(pd.DataFrame(st.session_state.evidence_writing_entries), use_container_width=True, hide_index=True)
    st.download_button("Export writing notes", export_entries(st.session_state.evidence_writing_entries), "evidence_grounded_writing.md", "text/markdown")

st.info("Integrity rule: no evidence supplied → no evidence-backed draft. The tool does not fabricate results, citations, mechanisms, or statistical significance.")
