"""SciMantra Research OS — Research Impact & Reuse Engine."""
import pandas as pd
import streamlit as st
from src.scimantra.research_impact_reuse import OUTPUT_TYPES, PRIORITIES, audit, next_actions

st.set_page_config(page_title="Research Impact & Reuse",page_icon="📈",layout="wide")
st.title("📈 Research Impact & Reuse Engine")
st.caption("Turn completed research outputs into a structured roadmap for future studies, applications and reusable assets.")
st.warning("This is an idea-planning tool. IP, patentability, commercial potential and scientific feasibility require specialist evaluation.")
if "impact_items" not in st.session_state: st.session_state.impact_items=[]

with st.form("impact_form"):
    c=st.columns(3)
    title=c[0].text_input("Research output / finding")
    kind=c[1].selectbox("Reuse pathway",OUTPUT_TYPES)
    priority=c[2].selectbox("Priority",PRIORITIES)
    basis=st.text_area("What makes this output reusable or worth extending?")
    next_step=st.text_area("Proposed next step")
    if st.form_submit_button("Add reuse opportunity",type="primary"):
        st.session_state.impact_items.append({"title":title,"type":kind,"priority":priority,"basis":basis,"next_step":next_step})

items=st.session_state.impact_items
r=audit(items)
a,b,c,d=st.columns(4); a.metric("Opportunities",r["total"]); b.metric("High priority",r["high"]); c.metric("Planned",r["planned"]); d.metric("Need next step",r["unplanned"])

st.subheader("Next actions")
for x in next_actions(items): st.write("→",x)

st.subheader("Research reuse map")
if items:
    df=pd.DataFrame(items); st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download reuse roadmap CSV",df.to_csv(index=False),"scimantra_research_reuse_roadmap.csv","text/csv")
else: st.info("Add a published finding, method, dataset, figure, result or research question to begin mapping reuse opportunities.")

st.subheader("Suggested strategy")
st.write("Prioritize opportunities that are strongly connected to your evidence, feasible with available resources, and capable of producing a clearly differentiated research question. Treat patent/IP and commercialization routes as separate specialist assessments.")
st.caption("Module 93 · Research impact, reuse and next-study planning layer.")
