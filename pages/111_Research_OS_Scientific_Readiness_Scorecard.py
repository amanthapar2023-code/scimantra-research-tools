"""Phase 111 — Scientific Readiness Scorecard."""
import pandas as pd
import streamlit as st
from scimantra.research_os_scientific_audit import DOMAINS, LEVELS, actions, export_markdown, readiness, score

st.set_page_config(page_title="SciMantra — Scientific Readiness", page_icon="🛡️", layout="wide")
st.title("🛡️ Phase 111 — Scientific Readiness Scorecard")
st.caption("One transparent view of the major scientific-readiness audits before manuscript or submission decisions.")
st.info("This scorecard fuses researcher-supplied audit levels. It is decision support, not a scientific validity certificate, peer-review prediction, or publication guarantee.")

if "research_os_audit_signals" not in st.session_state: st.session_state.research_os_audit_signals = {d:"Not assessed" for d in DOMAINS}
with st.form("scorecard"):
    for i in range(0,len(DOMAINS),2):
        cols=st.columns(2)
        for j,col in enumerate(cols):
            if i+j < len(DOMAINS):
                d=DOMAINS[i+j]
                st.session_state.research_os_audit_signals[d]=col.selectbox(d,LEVELS,index=LEVELS.index(st.session_state.research_os_audit_signals[d]),key=f"audit_{i+j}")
    submitted=st.form_submit_button("🔎 Calculate readiness",type="primary")

signals=[{"domain":d,"level":v} for d,v in st.session_state.research_os_audit_signals.items()]
r=score(signals)
a,b,c,d=st.columns(4)
a.metric("Readiness score",f"{r['score']} / 100"); b.metric("Assessed",f"{r['assessed']} / {r['total_domains']}"); c.metric("Critical gaps",r['critical']); d.metric("Needs work",r['needs_work'])
st.progress(r['score']/100)
if r['critical']: st.error("Critical scientific-readiness gaps remain.")
elif r['assessed'] < r['total_domains']: st.warning("Assessment is incomplete; do not interpret the score as final readiness.")
elif r['needs_work']: st.warning("Some assessed domains still need improvement.")
else: st.success(readiness(r))

st.subheader("Readiness matrix")
st.dataframe(pd.DataFrame(r["rows"]),use_container_width=True,hide_index=True)
st.subheader("Priority actions")
acts=actions(r)
if acts:
    for x in acts: st.write("• "+x)
else: st.success("No unresolved scorecard actions from the entered signals.")

st.download_button("⬇️ Export scorecard Markdown",export_markdown(r),file_name="scimantra_scientific_readiness.md",mime="text/markdown")
st.divider(); st.caption("Use the underlying dedicated audit modules for domain-specific evidence and remediation. This layer only fuses their explicit states.")
