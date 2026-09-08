import streamlit as st
import pandas as pd
from src.scimantra.reviewer_attack import attack, attack_score

st.set_page_config(page_title="Reviewer Attack Simulator | SciMantra", page_icon="🛡️", layout="wide")
st.title("🛡️ Reviewer Attack Simulator")
st.caption("Try to break the study before a real reviewer does.")

title = st.text_input("Research title", value=st.session_state.get("ri_title", ""))
method = st.text_area("Method / design summary", placeholder="Paste your planned or actual design…")
result = st.text_area("Results / main claim summary (optional)")

if st.button("🔥 Attack my study", type="primary"):
    st.session_state.reviewer_rows = attack(title, method, result)

rows = st.session_state.get("reviewer_rows", [])
if rows:
    resolved = set()
    for row in rows:
        key = "resolved_" + row["Attack area"].lower().replace(" ", "_")
        if st.checkbox("I have addressed: " + row["Attack area"], key=key):
            resolved.add(row["Attack area"])
    score = attack_score(rows, resolved)
    a, b, c = st.columns(3)
    a.metric("Reviewer attacks", score["total"])
    b.metric("Addressed", score["resolved"])
    c.metric("Readiness", f"{score['readiness_percent']}%")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button("Download reviewer attack report", pd.DataFrame(rows).to_csv(index=False), "reviewer_attack_report.csv", "text/csv")
else:
    st.info("Enter your design and results summary, then launch the adversarial review.")

st.warning("This is a structured pre-submission audit, not a prediction of peer-review outcome. It deliberately raises questions rather than inventing flaws or scientific facts.")
