import streamlit as st
import pandas as pd
from src.scimantra.research_audit import audit_title, build_reviewer_questions, claim_check, risk_score

st.set_page_config(page_title="Research Audit | SciMantra", page_icon="🛡️", layout="wide")
st.title("🛡️ Research Audit & Reviewer Simulator")
st.caption("Try to break the study before a reviewer does.")

title = st.text_input("Research title", placeholder="Enter your research title")
if title.strip():
    audit = audit_title(title)
    st.subheader("Research risk radar")
    done = {}
    rows=[]
    for label, flag in audit["flags"]:
        done[label] = st.checkbox(f"Addressed: {label}", key="audit_"+str(abs(hash(label))))
        rows.append({"Audit area":label,"Risk / question":flag,"Addressed":done[label]})
    score = risk_score(audit, done)
    st.metric("Audit completion", f"{score}%")
    if score < 60: st.error("Major unresolved audit items")
    elif score < 85: st.warning("Several reviewer vulnerabilities remain")
    else: st.success("Strong pre-review readiness — verify against the actual study")

    st.divider()
    st.subheader("🧑‍⚖️ Skeptical reviewer mode")
    for i,q in enumerate(build_reviewer_questions(title),1):
        st.markdown(f"**Reviewer {i}.** {q}")
        st.text_area("Your defence / evidence", key=f"def_{i}", height=70)

    st.divider()
    st.subheader("🔎 Claim stress test")
    claim=st.text_area("Paste one important manuscript claim")
    if st.button("Stress-test claim") and claim.strip():
        result=claim_check(claim)
        st.write("Evidence status:", result["evidence_status"])
        for q in result["checks"]: st.markdown(f"- {q}")

    st.download_button("⬇️ Export audit", pd.DataFrame(rows).to_csv(index=False).encode(), "scimantra_research_audit.csv", "text/csv")
else:
    st.info("Enter a title to start the audit.")
