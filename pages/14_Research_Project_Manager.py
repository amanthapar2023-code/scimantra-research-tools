import io
import json
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="SciMantra Research Project Manager", page_icon="📁", layout="wide")
st.title("📁 SciMantra Research Project Manager")
st.caption("Keep your research project, experiments, datasets, milestones and documentation organized in one workspace.")

if "rpm_project" not in st.session_state:
    st.session_state.rpm_project = {
        "name": "Untitled Research Project",
        "researcher": "",
        "institution": "",
        "objective": "",
        "status": "Planning",
        "start_date": datetime.now().date().isoformat(),
        "notes": "",
        "experiments": [],
        "datasets": [],
        "milestones": [],
    }

p = st.session_state.rpm_project

with st.sidebar:
    st.header("Project")
    p["name"] = st.text_input("Project name", p["name"])
    p["researcher"] = st.text_input("Researcher / PI", p["researcher"])
    p["institution"] = st.text_input("Institution / Lab", p["institution"])
    p["status"] = st.selectbox("Status", ["Planning", "Active", "Analysis", "Manuscript", "Completed"], index=["Planning", "Active", "Analysis", "Manuscript", "Completed"].index(p["status"]))

module = st.selectbox("Workspace", [
    "📊 Project Dashboard",
    "🧪 Experiments",
    "📂 Datasets",
    "📅 Milestones",
    "📝 Project Notes",
    "📦 Export Project",
])

if module == "📊 Project Dashboard":
    st.subheader("Project overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Experiments", len(p["experiments"]))
    c2.metric("Datasets", len(p["datasets"]))
    c3.metric("Milestones", len(p["milestones"]))
    completed = sum(x.get("done", False) for x in p["milestones"])
    c4.metric("Milestones complete", f"{completed}/{len(p['milestones'])}")

    p["objective"] = st.text_area("Research objective", p["objective"], height=120)
    st.info(f"**Status:** {p['status']}  •  **Started:** {p['start_date']}")
    if p["experiments"]:
        st.markdown("### Recent experiments")
        st.dataframe(pd.DataFrame(p["experiments"]), width="stretch", hide_index=True)
    if p["milestones"]:
        st.markdown("### Milestone progress")
        for m in p["milestones"]:
            st.checkbox(m["name"], value=m.get("done", False), key=f"dash_{m['id']}")

elif module == "🧪 Experiments":
    st.subheader("Experiment registry")
    with st.form("experiment_form"):
        name = st.text_input("Experiment name")
        design = st.text_input("Design / comparison")
        date = st.date_input("Experiment date", value=datetime.now().date())
        replicates = st.number_input("Biological replicates", min_value=1, value=3)
        outcome = st.text_input("Primary outcome")
        add = st.form_submit_button("➕ Add experiment")
    if add:
        p["experiments"].append({
            "Experiment": name or f"Experiment {len(p['experiments'])+1}",
            "Design": design,
            "Date": date.isoformat(),
            "Biological replicates": int(replicates),
            "Primary outcome": outcome,
        })
        st.rerun()
    if p["experiments"]:
        df = pd.DataFrame(p["experiments"])
        st.dataframe(df, width="stretch", hide_index=True)
        if st.button("Clear experiment registry"):
            p["experiments"] = []
            st.rerun()

elif module == "📂 Datasets":
    st.subheader("Dataset registry")
    upload = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
    if upload:
        try:
            df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
            st.session_state.rpm_current_df = df
            entry = {
                "File": upload.name,
                "Rows": int(df.shape[0]),
                "Columns": int(df.shape[1]),
                "Missing cells": int(df.isna().sum().sum()),
                "Registered": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            if not any(x["File"] == upload.name for x in p["datasets"]):
                p["datasets"].append(entry)
            st.success(f"Loaded {upload.name}")
            st.dataframe(df.head(100), width="stretch", hide_index=True)
        except Exception as exc:
            st.error(f"Could not read dataset: {exc}")
    if p["datasets"]:
        st.markdown("### Registered datasets")
        st.dataframe(pd.DataFrame(p["datasets"]), width="stretch", hide_index=True)

elif module == "📅 Milestones":
    st.subheader("Project milestones")
    with st.form("milestone_form"):
        name = st.text_input("Milestone")
        due = st.date_input("Target date", value=datetime.now().date())
        add = st.form_submit_button("➕ Add milestone")
    if add:
        p["milestones"].append({"id": len(p["milestones"])+1, "name": name or f"Milestone {len(p['milestones'])+1}", "due": due.isoformat(), "done": False})
        st.rerun()
    for m in p["milestones"]:
        m["done"] = st.checkbox(f"{m['name']} — target {m['due']}", value=m.get("done", False), key=f"mile_{m['id']}")
    if p["milestones"] and st.button("Clear milestones"):
        p["milestones"] = []
        st.rerun()

elif module == "📝 Project Notes":
    st.subheader("Research notebook")
    p["notes"] = st.text_area("Notes, decisions, observations and protocol deviations", p["notes"], height=400, placeholder="Record important decisions and observations here...")
    st.download_button("⬇️ Download notes", p["notes"].encode("utf-8"), "scimantra_project_notes.txt", "text/plain")

else:
    st.subheader("Export complete project record")
    project_json = json.dumps(p, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button("⬇️ Download project JSON", project_json, "scimantra_project_record.json", "application/json")

    summary = io.StringIO()
    summary.write(f"SciMantra Research Project\n{'='*30}\n")
    summary.write(f"Project: {p['name']}\nResearcher/PI: {p['researcher']}\nInstitution/Lab: {p['institution']}\nStatus: {p['status']}\nStart date: {p['start_date']}\n\n")
    summary.write(f"Objective\n---------\n{p['objective']}\n\nExperiments\n-----------\n")
    for x in p["experiments"]:
        summary.write(f"- {x}\n")
    summary.write("\nDatasets\n--------\n")
    for x in p["datasets"]:
        summary.write(f"- {x}\n")
    summary.write("\nMilestones\n----------\n")
    for x in p["milestones"]:
        summary.write(f"- [{'x' if x.get('done') else ' '}] {x['name']} — {x['due']}\n")
    summary.write(f"\nNotes\n-----\n{p['notes']}\n")
    st.text_area("Project record preview", summary.getvalue(), height=450)
    st.download_button("⬇️ Download project summary", summary.getvalue().encode("utf-8"), "scimantra_project_summary.txt", "text/plain")

st.divider()
st.caption("Current version stores the workspace in the active Streamlit session. Persistent multi-user cloud storage, authentication and collaboration are planned for the account layer.")
