"""Phase 105 — Research OS Workflow Runner."""
import pandas as pd
import streamlit as st

from scimantra.research_os_data_bus import new_bus, snapshot
from scimantra.research_os_workflow_runner import STATUSES, WORKFLOWS, advance, audit_run, export_run, link_step_artifacts, new_run

st.set_page_config(page_title="SciMantra — Workflow Runner", page_icon="▶️", layout="wide")
st.title("▶️ Phase 105 — Research OS Workflow Runner")
st.caption("Chain registered research outputs through explicit, human-confirmed research workflows.")
st.info("The runner orchestrates project state and artifact links only. It does not automatically execute experiments, invent results, or certify scientific validity.")

if "research_os_bus" not in st.session_state:
    st.session_state.research_os_bus = new_bus()
if "research_os_workflow_run" not in st.session_state:
    st.session_state.research_os_workflow_run = new_run("Full Research Cycle", st.session_state.research_os_bus.get("project", {}))

bus = st.session_state.research_os_bus
run = st.session_state.research_os_workflow_run

with st.sidebar:
    st.subheader("Workflow")
    workflow_id = st.selectbox("Recipe", list(WORKFLOWS), index=list(WORKFLOWS).index(run["workflow_id"]) if run["workflow_id"] in WORKFLOWS else 0)
    if workflow_id != run["workflow_id"]:
        if st.button("Start selected workflow", type="primary"):
            st.session_state.research_os_workflow_run = new_run(workflow_id, bus.get("project", {})); st.rerun()
    st.divider()
    st.metric("Registered bus artifacts", len(bus.get("artifacts", [])))
    st.caption("Use Phase 104 to register tool outputs before assigning them to workflow steps.")

audit = audit_run(run, bus)
a, b, c, d = st.columns(4)
a.metric("Completion", f"{audit['completion_pct']}%")
b.metric("Complete", audit["complete"])
c.metric("Ready", len(audit["ready"]))
d.metric("Blocked", len(audit["blocked"]))
st.progress(audit["completion_pct"] / 100 if audit["steps"] else 0)

st.subheader(f"{run['workflow_id']} · {run['run_id']}")
st.caption("A step becomes operationally ready when its dependencies are complete and its referenced input artifacts exist on the shared bus.")

artifact_options = [a.get("id") for a in bus.get("artifacts", []) if a.get("id")]

for step in run["steps"]:
    with st.container(border=True):
        top = st.columns([0.55, 2.2, 1.4, 1.4])
        top[0].markdown(f"### {step['order']}")
        top[1].markdown(f"**{step['name']}**  \n`{step['stage']}` · {step['tool']}")
        current = step["status"]
        new_status = top[2].selectbox("Status", STATUSES, index=STATUSES.index(current), key=f"wf_status_{step['order']}")
        if new_status != current:
            st.session_state.research_os_workflow_run = advance(run, step["id"], new_status); run = st.session_state.research_os_workflow_run; st.rerun()
        top[3].metric("Dependencies", len(step["dependencies"]))
        if step["dependencies"]:
            st.caption("Depends on: " + ", ".join(step["dependencies"]))
        c1, c2 = st.columns(2)
        with c1:
            inputs = st.multiselect("Input artifacts", artifact_options, default=[x for x in step.get("input_artifact_ids", []) if x in artifact_options], key=f"wf_in_{step['order']}")
        with c2:
            outputs = st.multiselect("Output artifacts", artifact_options, default=[x for x in step.get("output_artifact_ids", []) if x in artifact_options], key=f"wf_out_{step['order']}")
        note = st.text_input("Researcher note", value=step.get("note", ""), key=f"wf_note_{step['order']}")
        if st.button("Save step + link artifacts", key=f"wf_save_{step['order']}"):
            updated = advance(run, step["id"], new_status, inputs, outputs, note)
            try:
                linked = link_step_artifacts(updated, bus, step["id"])
                st.session_state.research_os_workflow_run = updated
                st.session_state.research_os_bus = linked
                st.success("Step state saved and selected artifact relationships recorded.")
                st.rerun()
            except Exception as exc:
                st.session_state.research_os_workflow_run = updated
                st.error(str(exc))

st.divider()
st.subheader("🔎 Workflow audit")
audit = audit_run(st.session_state.research_os_workflow_run, st.session_state.research_os_bus)
if audit["issues"]:
    st.warning(f"{len(audit['issues'])} issue(s) require attention.")
    st.dataframe(pd.DataFrame(audit["issues"]), use_container_width=True, hide_index=True)
else:
    st.success("No structural workflow issues detected.")
if audit["ready"]:
    st.write("**Next available steps:** " + ", ".join(audit["ready"]))
if audit["ready_to_finish"]:
    st.success("Workflow run is structurally complete.")

with st.expander("Workflow recipe"):
    st.dataframe(pd.DataFrame([{**s, "dependencies": ", ".join(s["dependencies"])} for s in run["steps"]]), use_container_width=True, hide_index=True)

st.subheader("💾 Run snapshot")
st.download_button("⬇️ Export workflow run JSON", export_run(st.session_state.research_os_workflow_run, st.session_state.research_os_bus), file_name="scimantra_workflow_run.json", mime="application/json")
st.download_button("⬇️ Export shared bus JSON", snapshot(st.session_state.research_os_bus), file_name="scimantra_research_os_bus.json", mime="application/json")
st.caption("Phase 105 boundary: transparent workflow orchestration. Human confirmation remains required for scientific outputs and transitions.")
