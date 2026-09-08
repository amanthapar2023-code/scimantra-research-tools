import streamlit as st
import pandas as pd
from src.scimantra.evidence_matrix import FIELDS, empty_record, evidence_status, matrix_score, gap_candidates

st.set_page_config(page_title="Evidence Matrix Workbench | SciMantra", page_icon="📚", layout="wide")
st.title("📚 Evidence Matrix Workbench")
st.caption("Build the literature matrix behind your Introduction and research-gap argument.")

if "em_records" not in st.session_state:
    st.session_state.em_records = [empty_record() for _ in range(5)]

count = st.number_input("Number of anchor papers", min_value=1, max_value=20, value=len(st.session_state.em_records), step=1)
if count != len(st.session_state.em_records):
    records = st.session_state.em_records[:count]
    while len(records) < count: records.append(empty_record())
    st.session_state.em_records = records

for i, record in enumerate(st.session_state.em_records):
    with st.expander(f"Paper {i+1}: {record.get('Paper') or 'Add paper'}", expanded=i == 0):
        record["Paper"] = st.text_input("Paper title / identifier", value=record.get("Paper", ""), key=f"paper_{i}")
        cols = st.columns(2)
        for j, field in enumerate(FIELDS):
            if field == "Confidence":
                continue
            record[field] = cols[j % 2].text_area(field, value=record.get(field, ""), key=f"{field}_{i}", height=75)
        record["Confidence"] = st.selectbox("Confidence", ["Unverified", "Researcher verified", "Source anchored"], index=["Unverified", "Researcher verified", "Source anchored"].index(record.get("Confidence", "Unverified")), key=f"conf_{i}")
        st.caption("Status: " + evidence_status(record))

score = matrix_score(st.session_state.em_records)
st.divider()
c1,c2=st.columns(2)
c1.metric("Matrix coverage", f"{score['coverage']}%")
c2.metric("Source-anchored papers", f"{score['source_anchored']}%")

st.subheader("🕳️ Evidence gaps in the matrix")
for gap in gap_candidates(st.session_state.em_records): st.warning(gap)

st.subheader("Export")
df=pd.DataFrame(st.session_state.em_records)
st.download_button("⬇️ Download full literature matrix", df.to_csv(index=False).encode(), "scimantra_literature_evidence_matrix.csv", "text/csv", use_container_width=True)
st.info("Rule: an empty cell is a missing evidence field, not an invitation for AI to guess. Source-anchored entries should point to a paper section, page, table, figure, DOI, or other verifiable location.")
