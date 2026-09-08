import streamlit as st
import pandas as pd
from src.scimantra.methodology_designer import design_from_title, audit_design, design_score, reviewer_challenges

st.set_page_config(page_title="Methodology Designer | SciMantra", page_icon="🧪", layout="wide")
st.title("🧪 Methodology Designer & Experimental Design Auditor")
st.caption("Turn a research question into an auditable study-design specification before collecting data.")

if "method_design" not in st.session_state:
    st.session_state.method_design = design_from_title("")

title = st.text_input("Research title / study question", value=st.session_state.get("ri_title", ""))
if st.button("Build methodology blueprint", type="primary", use_container_width=True):
    st.session_state.method_design = design_from_title(title)
    st.session_state.method_title = title

design = st.session_state.method_design

st.info("This is a planning and bias-audit layer. It does not invent a sample size, experimental result, or claim that a design is scientifically valid for your specific field.")

left, right = st.columns(2)
fields = list(design.keys())
for i, key in enumerate(fields):
    target = left if i % 2 == 0 else right
    label = key.replace("_", " ").title()
    design[key] = target.text_area(label, value=str(design[key]), key=f"method_{key}", height=90)

st.session_state.method_design = design

st.divider()
st.subheader("🔎 Experimental Design Audit")
audit = audit_design(design)
score = design_score(audit)
a, b, c = st.columns(3)
a.metric("Design readiness", f"{score['score']}%")
b.metric("Checks addressed", f"{score['present']}/{score['total']}")
c.metric("Checks needing detail", f"{score['total'] - score['present']}")

st.dataframe(pd.DataFrame(audit), use_container_width=True, hide_index=True)

st.subheader("🧑‍⚖️ Reviewer challenge questions")
for q in reviewer_challenges(design):
    st.write("• " + q)

export = pd.DataFrame(audit).to_csv(index=False).encode()
st.download_button("⬇️ Export design audit", export, "scimantra_experimental_design_audit.csv", "text/csv", use_container_width=True)
st.success("Design principle: every important conclusion should have a pre-specified measurement, comparator, replication structure, and analysis path.")
