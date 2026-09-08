import streamlit as st
import pandas as pd
from src.scimantra.evidence_matrix import empty_record
from src.scimantra.introduction_architect import build_introduction_blueprint, render_markdown

st.set_page_config(page_title="Introduction Architect | SciMantra", page_icon="✍️", layout="wide")
st.title("✍️ Introduction Architect + Research Gap Engine")
st.caption("Turn your verified literature matrix into an evidence-traceable Introduction plan — not fabricated prose.")

records = st.session_state.get("em_records", [])
if not records:
    st.info("Start in **Evidence Matrix Workbench** and enter your anchor papers. You can also add a small matrix here.")
    n = st.number_input("Number of papers", 1, 20, 3)
    records = [empty_record() for _ in range(n)]

with st.expander("Import / edit matrix", expanded=not bool(st.session_state.get("em_records"))):
    title = st.text_input("Research title", value=st.session_state.get("ri_title", ""))
    for i, record in enumerate(records):
        with st.expander(f"Paper {i+1}: {record.get('Paper') or 'Add paper'}", expanded=i == 0):
            record["Paper"] = st.text_input("Paper title / identifier", record.get("Paper", ""), key=f"ia_paper_{i}")
            cols = st.columns(2)
            for j, field in enumerate(["Problem", "Challenges", "Research solution", "Technology / approach", "Innovation", "Difference from previous work", "Research gap", "Method", "Key result", "Limitation", "Evidence location"]):
                record[field] = cols[j % 2].text_area(field, record.get(field, ""), key=f"ia_{field}_{i}", height=68)

if st.button("🧠 Build Introduction + Detect Gaps", type="primary", width="stretch"):
    if not title.strip():
        st.error("Enter a research title first.")
    else:
        st.session_state.ia_blueprint = build_introduction_blueprint(title, records)

bp = st.session_state.get("ia_blueprint")
if bp:
    st.divider()
    st.subheader("Research-gap radar")
    gaps = bp["candidate_gaps"]
    if not gaps:
        st.success("No candidate pattern detected from the supplied fields. This is not evidence that no gap exists.")
    for g in gaps:
        with st.container(border=True):
            st.markdown(f"**{g['type']}**")
            st.write(g["finding"])
            st.caption("Evidence pattern: " + g["evidence"])
            st.info("Verification step: " + g["action"])

    st.subheader("Introduction architecture")
    for section in bp["sections"]:
        with st.expander(section["section"], expanded=section["section"] in {"Problem", "What is still missing"}):
            st.caption(section["purpose"])
            if section["evidence"]:
                st.markdown("**Evidence blocks to synthesize:**")
                for item in section["evidence"]:
                    location = item["location"] or "LOCATION NEEDED"
                    st.markdown(f"- **{item['paper']}** — {item['text']}  \n  `Evidence: {location}`")
            else:
                st.warning("No evidence supplied. Write this section only after collecting and verifying sources.")

    st.subheader("📄 Drafting blueprint")
    st.code(render_markdown(bp), language="markdown")
    st.download_button("⬇️ Export Introduction blueprint", render_markdown(bp).encode("utf-8"), "scimantra_introduction_blueprint.md", "text/markdown", width="stretch")

    if bp["result_evidence_present"]:
        st.warning("Key-result fields exist in the matrix. Treat them as source material only after researcher verification and source anchoring.")
    else:
        st.info("No results supplied. The Introduction Architect will not manufacture Results or Discussion claims.")

st.divider()
st.caption("SciMantra integrity rule: candidate gaps are patterns for verification, not declarations of novelty. Every publishable claim should be traceable to a source or to the researcher's own verified data.")
