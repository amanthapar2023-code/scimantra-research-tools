import json
from datetime import datetime

import streamlit as st

from src.scimantra.account import new_project, project_summary, touch

st.set_page_config(page_title="SciMantra Accounts & Projects", page_icon="🔐", layout="wide")
st.title("🔐 SciMantra Accounts & Project Hub")
st.caption("Account-ready project management foundation for researchers, labs and future team collaboration.")

# This is intentionally a foundation: authentication credentials must be handled
# by a proper identity provider/database, not by this Streamlit session.
if "account_profile" not in st.session_state:
    st.session_state.account_profile = {"name": "", "email": "", "institution": ""}
if "projects" not in st.session_state:
    st.session_state.projects = []
if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None

profile = st.session_state.account_profile

with st.sidebar:
    st.header("Researcher profile")
    profile["name"] = st.text_input("Name", profile["name"])
    profile["email"] = st.text_input("Email", profile["email"])
    profile["institution"] = st.text_input("Institution / Lab", profile["institution"])
    st.divider()
    st.caption("Authentication status")
    st.success("Session active")
    st.caption("Production authentication will use a managed identity provider.")

if not st.session_state.projects:
    st.info("No projects yet. Create your first research project below.")

left, right = st.columns([2, 1])
with left:
    st.subheader("Your research projects")
    if st.session_state.projects:
        rows = [project_summary(x) for x in st.session_state.projects]
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.write("Create a project to begin organizing experiments and datasets.")

with right:
    st.subheader("Create project")
    with st.form("new_project"):
        project_name = st.text_input("Project name", placeholder="e.g. H₂S biodegradation study")
        project_status = st.selectbox("Initial status", ["Planning", "Active", "Analysis", "Manuscript"])
        create = st.form_submit_button("➕ Create project", type="primary")
    if create:
        project = new_project(project_name, profile.get("email", ""))
        project["status"] = project_status
        st.session_state.projects.append(project)
        st.session_state.active_project_id = project["id"]
        st.rerun()

if st.session_state.projects:
    st.divider()
    ids = [x["id"] for x in st.session_state.projects]
    labels = {x["id"]: x["name"] for x in st.session_state.projects}
    default = ids.index(st.session_state.active_project_id) if st.session_state.active_project_id in ids else 0
    selected = st.selectbox("Active project", ids, index=default, format_func=lambda x: labels[x])
    st.session_state.active_project_id = selected
    project = next(x for x in st.session_state.projects if x["id"] == selected)

    st.subheader("Active project")
    c1, c2, c3, c4 = st.columns(4)
    summary = project_summary(project)
    c1.metric("Experiments", summary["experiments"])
    c2.metric("Datasets", summary["datasets"])
    c3.metric("Milestones", summary["milestones"])
    c4.metric("Completed", f"{summary['completed_milestones']}/{summary['milestones']}")

    with st.form("project_edit"):
        name = st.text_input("Project name", project["name"])
        status = st.selectbox("Status", ["Planning", "Active", "Analysis", "Manuscript", "Completed"], index=["Planning", "Active", "Analysis", "Manuscript", "Completed"].index(project.get("status", "Planning")))
        objective = st.text_area("Research objective", project.get("objective", ""), height=120)
        save = st.form_submit_button("💾 Save project")
    if save:
        project["name"] = name.strip() or project["name"]
        project["status"] = status
        project["objective"] = objective
        project.update(touch(project))
        st.success("Project updated for this session.")

    st.markdown("### Account/project architecture")
    st.info("The current layer keeps projects in the active session. The next production layer can connect this same model to PostgreSQL/Supabase/Firebase and a managed authentication provider, giving each researcher private projects and enabling team sharing.")

    export = json.dumps(project, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button("⬇️ Export active project JSON", export, "scimantra_active_project.json", "application/json")

st.divider()
st.warning("Security note: do not enter passwords, API keys or payment information into this page. Passwords and authentication tokens should be handled by a dedicated identity provider, never stored in Streamlit session state or source code.")
