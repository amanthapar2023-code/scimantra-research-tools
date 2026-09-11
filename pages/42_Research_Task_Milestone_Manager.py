"""SciMantra Research Task & Milestone Manager.

Turns project evidence gaps, review actions, experiments, manuscript work and
submission requirements into traceable, actionable tasks.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json

import pandas as pd
import streamlit as st

from src.scimantra import cloud

st.title("🗂️ Research Task & Milestone Manager")
st.caption("Turn research gaps into accountable next actions — without changing the scientific evidence.")

try:
    supa = cloud.client(st.secrets)
except Exception:
    supa = None

if supa is None:
    st.info("Cloud project mode is not configured. Connect Supabase in Streamlit secrets to use persistent project tasks.")
    st.stop()

user = cloud.current_user(supa)
if not user:
    st.warning("Please sign in to use the Research Task & Milestone Manager.")
    st.stop()

projects = cloud.list_projects(supa, user.id)
if not projects:
    st.info("Create a research project first in the Cloud Project Workspace.")
    st.stop()

project_names = [p.get("name", "Unnamed project") for p in projects]
selected_name = st.selectbox("Active project", project_names)
project = projects[project_names.index(selected_name)]
project_id = project["id"]

# Tasks are stored as immutable, provenance-bearing Vault records.  The latest
# record for each task_id is the active state.
def load_tasks() -> list[dict]:
    rows = cloud.list_artifacts(supa, project_id)
    latest: dict[str, dict] = {}
    for row in rows:
        if row.get("artifact_type") != "research_task":
            continue
        prov = row.get("provenance_json") or {}
        task_id = prov.get("task_id")
        if not task_id:
            continue
        if task_id not in latest:
            latest[task_id] = dict(prov.get("task", {}), task_id=task_id, artifact_id=row.get("id"), created_at=row.get("created_at"))
    return list(latest.values())


def save_task(task: dict) -> bool:
    payload = {k: v for k, v in task.items() if k != "artifact_id"}
    raw = json.dumps(payload, sort_keys=True, default=str).encode()
    digest = hashlib.sha256(raw).hexdigest()
    name = f"task_{task['task_id']}_{digest[:12]}.json"
    try:
        path = cloud.upload_project_file(supa, user.id, project_id, name, raw, "application/json")
        cloud.create_artifact(
            supa, user.id, project_id, name, "research_task", path,
            "application/json", len(raw), digest, "Research Task & Milestone Manager",
            {"task_id": task["task_id"], "task": payload, "record_type": "task_state"},
        )
        return True
    except Exception as exc:
        st.error(f"Could not save task: {exc}")
        return False


tasks = load_tasks()

# Pull existing project milestones and turn unfinished milestones into suggested actions.
try:
    milestones = cloud.list_milestones(supa, project_id)
except Exception:
    milestones = []

open_milestones = [m for m in milestones if not m.get("completed")]

with st.expander("➕ Create research task", expanded=not tasks):
    c1, c2 = st.columns([2, 1])
    title = c1.text_input("Task title", placeholder="e.g., Verify replicate balance before final analysis")
    category = c2.selectbox("Category", ["Evidence", "Review", "Experiment", "Analysis", "Figure", "Manuscript", "Submission", "Data quality", "Other"])
    c1, c2, c3 = st.columns(3)
    priority = c1.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
    status = c2.selectbox("Status", ["Backlog", "Ready", "In Progress", "Blocked", "Done"])
    linked_stage = c3.selectbox("Linked stage", ["Dataset", "Quality", "Statistics", "Evidence", "Figures", "Manuscript", "Submission", "Package", "Other"])
    c1, c2 = st.columns(2)
    owner = c1.text_input("Owner / assignee", value="")
    due = c2.date_input("Due date", value=date.today())
    notes = st.text_area("Action notes / acceptance criteria", placeholder="What must be completed or verified before this task can be marked Done?")
    if st.button("Save task", type="primary", disabled=not title.strip()):
        task = {
            "task_id": hashlib.sha256(f"{project_id}|{title}|{date.today()}".encode()).hexdigest()[:16],
            "title": title.strip(), "category": category, "priority": priority,
            "status": status, "linked_stage": linked_stage, "owner": owner.strip(),
            "due_date": str(due), "notes": notes.strip(), "project_id": project_id,
        }
        if save_task(task):
            st.success("Task saved to the project Vault.")
            st.rerun()

# Metrics

today = date.today()
for t in tasks:
    try:
        t["overdue"] = t.get("status") != "Done" and bool(t.get("due_date")) and date.fromisoformat(str(t["due_date"])) < today
    except ValueError:
        t["overdue"] = False

counts = {s: sum(t.get("status") == s for t in tasks) for s in ["Backlog", "Ready", "In Progress", "Blocked", "Done"]}
overdue = sum(bool(t.get("overdue")) for t in tasks)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", len(tasks))
c2.metric("Open", len(tasks) - counts["Done"])
c3.metric("In progress", counts["In Progress"])
c4.metric("Blocked", counts["Blocked"])
c5.metric("Overdue", overdue)

if open_milestones:
    st.info(f"{len(open_milestones)} open project milestone(s) are available as planning signals. They are not automatically marked complete by task status.")

if not tasks:
    st.markdown("### Start with the next action")
    st.write("Create a task for the most important evidence gap, review action, experiment, analysis, manuscript correction, or submission requirement.")
    st.stop()

st.markdown("### Task board")
f1, f2, f3 = st.columns(3)
filter_status = f1.multiselect("Status", ["Backlog", "Ready", "In Progress", "Blocked", "Done"], default=[])
filter_priority = f2.multiselect("Priority", ["Critical", "High", "Medium", "Low"], default=[])
filter_category = f3.multiselect("Category", sorted({t.get("category", "Other") for t in tasks}), default=[])

visible = [t for t in tasks if (not filter_status or t.get("status") in filter_status) and (not filter_priority or t.get("priority") in filter_priority) and (not filter_category or t.get("category") in filter_category)]
visible.sort(key=lambda t: (t.get("status") == "Done", t.get("due_date", "9999-12-31"), t.get("priority", "Low")))

for task in visible:
    label = f"{task.get('priority','Medium')} · {task.get('category','Other')} · {task.get('linked_stage','Other')}"
    with st.expander(f"{'🔴 ' if task.get('overdue') else ''}{task.get('title','Untitled')} — {task.get('status','Backlog')}"):
        st.caption(label)
        c1, c2, c3 = st.columns(3)
        new_status = c1.selectbox("Status", ["Backlog", "Ready", "In Progress", "Blocked", "Done"], index=["Backlog", "Ready", "In Progress", "Blocked", "Done"].index(task.get("status", "Backlog")), key=f"status_{task['task_id']}")
        new_priority = c2.selectbox("Priority", ["Critical", "High", "Medium", "Low"], index=["Critical", "High", "Medium", "Low"].index(task.get("priority", "Medium")), key=f"priority_{task['task_id']}")
        new_owner = c3.text_input("Owner", value=task.get("owner", ""), key=f"owner_{task['task_id']}")
        st.write(f"**Due:** {task.get('due_date','—')}  |  **Stage:** {task.get('linked_stage','—')}")
        if task.get("notes"):
            st.write(task["notes"])
        if st.button("Save task update", key=f"save_{task['task_id']}"):
            updated = dict(task)
            updated.update(status=new_status, priority=new_priority, owner=new_owner.strip())
            updated.pop("artifact_id", None)
            if save_task(updated):
                st.success("Task state recorded with a new provenance record.")
                st.rerun()

st.markdown("### Export task ledger")
ledger = pd.DataFrame(visible)
if not ledger.empty:
    st.dataframe(ledger.drop(columns=["artifact_id"], errors="ignore"), width="stretch", hide_index=True)
    st.download_button("Download task ledger (CSV)", ledger.to_csv(index=False).encode("utf-8"), "research_task_ledger.csv", "text/csv")

st.divider()
st.caption("Scientific safeguard: task completion records workflow progress only. It does not establish statistical significance, validate a result, or replace scientific review.")
