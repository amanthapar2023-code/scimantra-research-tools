"""Phase 106 — Research OS Intelligent Next-Action Engine."""
import pandas as pd
import streamlit as st
from scimantra.research_os_data_bus import new_bus
from scimantra.research_os_next_action import export_markdown, recommend, summary
from scimantra.research_os_workflow_runner import WORKFLOWS, new_run, advance

st.set_page_config(page_title="SciMantra — Next Action", page_icon="🧭", layout="wide")
st.title("🧭 Phase 106 — Intelligent Next-Action Engine")
st.caption("Turn workflow state and research readiness signals into a prioritized action queue.")
st.info("Recommendations are transparent decision support. They do not infer scientific truth, invent results, or replace researcher judgment.")

if "research_os_bus" not in st.session_state: st.session_state.research_os_bus = new_bus()
if "research_os_workflow_run" not in st.session_state: st.session_state.research_os_workflow_run = new_run("Full Research Cycle", st.session_state.research_os_bus.get("project", {}))
run = st.session_state.research_os_workflow_run; bus = st.session_state.research_os_bus

with st.sidebar:
    st.subheader("Research context")
    workflow = st.selectbox("Workflow", list(WORKFLOWS), index=list(WORKFLOWS).index(run["workflow_id"]) if run["workflow_id"] in WORKFLOWS else 0)
    if workflow != run["workflow_id"] and st.button("Load workflow", type="primary"):
        st.session_state.research_os_workflow_run = new_run(workflow, bus.get("project", {})); st.rerun()
    st.caption(f"Project: {bus.get('project', {}).get('project', {}).get('name', 'My Research Project')}")

recs = recommend(run, bus)
s = summary(recs)
a,b,c,d = st.columns(4)
a.metric("Recommended actions", s["total"]); b.metric("Critical", s["critical"]); c.metric("High", s["high"]); d.metric("Top score", recs[0]["score"] if recs else 0)

if recs:
    top = recs[0]
    st.success(f"**Top next action:** {top['action']} — {top['priority']} priority ({top['score']}/100).")
    st.caption(top["reason"])
else: st.success("No incomplete workflow action is currently identified.")

st.divider()
tab1, tab2, tab3 = st.tabs(["Priority Queue", "Why this action?", "Export"])
with tab1:
    if recs: st.dataframe(pd.DataFrame(recs), use_container_width=True, hide_index=True)
    else: st.info("Complete or start a workflow in Phase 105 to generate actionable recommendations.")
with tab2:
    for r in recs[:8]:
        with st.container(border=True):
            st.markdown(f"**{r['priority']} · {r['score']}/100 — {r['action']}**")
            st.caption(f"Stage: {r['stage']} · Tool: {r['tool']}")
            st.write(r['reason'])
            if r['step_id'] != 'audit':
                step = next((x for x in run['steps'] if x['id'] == r['step_id']), None)
                if step and step['status'] == 'Not started' and st.button("Mark Ready", key=f"ready_{r['step_id']}"):
                    st.session_state.research_os_workflow_run = advance(run, r['step_id'], 'Ready'); st.rerun()
with tab3:
    st.download_button("⬇️ Export next-action queue", export_markdown(recs), file_name="scimantra_next_action_queue.md", mime="text/markdown")
    st.download_button("⬇️ Export JSON-ready table", pd.DataFrame(recs).to_csv(index=False), file_name="scimantra_next_actions.csv", mime="text/csv")

st.divider()
st.subheader("Decision principle")
st.write("The engine favors blocked/at-risk steps, completed dependencies, missing output records, and explicit audit signals. It ranks work; it does not decide whether a scientific conclusion is true.")
st.caption("Phase 106 boundary: prioritization and explainability only. Scientific decisions remain with the researcher.")
