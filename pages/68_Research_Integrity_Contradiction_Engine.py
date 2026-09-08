import pandas as pd
import streamlit as st
from scimantra.research_integrity import RECORD_TYPES, DIRECTIONS, audit_records, consistency_score, default_records, export_integrity

st.set_page_config(page_title="Research Integrity & Contradiction Engine | SciMantra", page_icon="🛡️", layout="wide")
st.title("🛡️ Research Integrity & Contradiction Engine")
st.caption("Cross-check claims, results, figures, tables, analyses and literature findings before they become a manuscript.")
st.warning("Integrity rule: this engine flags inconsistencies and missing verification. It does not decide which statement is scientifically true.")

records = st.session_state.get("integrity_records")
if records is None:
    records = default_records()
    st.session_state["integrity_records"] = records

st.subheader("1. Build the scientific consistency ledger")
for i, r in enumerate(records):
    with st.expander(f"{r['ID']} — {r['Type']} — {r['Topic']}", expanded=i < 2):
        c1, c2, c3 = st.columns(3)
        r["ID"] = c1.text_input("Record ID", r["ID"], key=f"ri_id_{i}")
        r["Type"] = c2.selectbox("Record type", RECORD_TYPES, index=RECORD_TYPES.index(r["Type"]), key=f"ri_type_{i}")
        r["Topic"] = c3.text_input("Comparison topic", r["Topic"], key=f"ri_topic_{i}")
        r["Statement"] = st.text_area("Exact statement", r.get("Statement", ""), key=f"ri_stmt_{i}", placeholder="Use the wording actually appearing in the paper, result output, figure/table interpretation, or verified source.")
        c1, c2, c3 = st.columns(3)
        r["Value"] = c1.text_input("Numeric value (optional)", r.get("Value", ""), key=f"ri_value_{i}")
        r["Unit"] = c2.text_input("Unit (optional)", r.get("Unit", ""), key=f"ri_unit_{i}")
        r["Direction"] = c3.selectbox("Direction", DIRECTIONS, index=DIRECTIONS.index(r.get("Direction", "Not assessed")), key=f"ri_dir_{i}")
        r["Source"] = st.text_input("Evidence / source anchor", r.get("Source", ""), key=f"ri_source_{i}", placeholder="Dataset ID, analysis output, Figure 2, Table 3, DOI, Methods section…")
        r["Status"] = st.selectbox("Verification status", ["Unverified", "Researcher confirmed", "Verified"], index=["Unverified", "Researcher confirmed", "Verified"].index(r.get("Status", "Unverified")), key=f"ri_status_{i}")
        r["Notes"] = st.text_area("Notes / reconciliation decision", r.get("Notes", ""), key=f"ri_notes_{i}")

c1, c2 = st.columns(2)
with c1:
    if st.button("➕ Add integrity record", type="primary", use_container_width=True):
        next_id = f"R{len(records)+1}"
        records.append({"ID":next_id,"Type":"Manuscript claim","Topic":"New topic","Statement":"","Value":"","Unit":"","Direction":"Not assessed","Source":"","Status":"Unverified","Notes":""})
        st.rerun()
with c2:
    if st.button("🗑️ Clear ledger", use_container_width=True):
        st.session_state.integrity_records = []
        st.rerun()

st.session_state.integrity_records = records
audit = audit_records(records)
score = consistency_score(audit)

st.subheader("2. Scientific consistency dashboard")
a,b,c,d = st.columns(4)
a.metric("Consistency score", f"{score}%")
b.metric("High-priority conflicts", audit["summary"]["high"])
c.metric("Moderate gaps", audit["summary"]["moderate"])
d.metric("Unanchored claims", audit["summary"]["unanchored_claims"])

if audit["issues"]:
    st.error("Review flags detected")
    st.dataframe(pd.DataFrame(audit["issues"]), use_container_width=True, hide_index=True)
else:
    st.success("No automatic conflict or missing-verification flag was triggered by the current ledger.")

st.subheader("3. Cross-artifact consistency check")
st.caption("Records with the same topic are compared. Opposite directions and different numeric values with the same unit are deliberately surfaced for human review.")
st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)

st.subheader("4. Researcher reconciliation checkpoint")
st.info("For every conflict: identify the authoritative source, check definitions/denominators/units/timepoints, document the reconciliation, and only then update the manuscript.")
reconcile = st.text_area("Global reconciliation notes", key="ri_global_notes", placeholder="Which source is authoritative? What did you verify? What changed in the manuscript?")

report = export_integrity(records, audit) + f"\n## Global reconciliation notes\n{reconcile.strip()}\n"
st.download_button("⬇️ Download integrity audit (Markdown)", report, "scimantra_research_integrity_audit.md", "text/markdown", use_container_width=True)

st.info("Important: a clean audit means only that this structured ledger found no flagged inconsistency. It is not a certificate of correctness, validity, absence of fabrication, or publication readiness.")
