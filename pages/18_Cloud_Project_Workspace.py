import pandas as pd
import streamlit as st

from src.scimantra.cloud import (
    client, configured, current_user, create_download_url, create_experiment, create_milestone,
    create_project, delete_project_file, list_experiments, list_milestones, list_project_datasets,
    list_projects, load_profile, register_dataset, save_profile, save_project,
    set_milestone_completed, subscription, upload_project_file,
)

st.set_page_config(page_title="SciMantra Cloud Workspace", page_icon="☁️", layout="wide")
st.title("☁️ SciMantra Cloud Research Workspace")
st.caption("Persistent project metadata and private research-file storage for authenticated researchers.")

if not configured(st.secrets):
    st.info("Cloud mode is not configured. Use the Research Project Manager for session-only projects, or configure Supabase using supabase/schema.sql.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa)
if user is None:
    st.warning("Please sign in from **👤 Login & Cloud Account** before opening the cloud workspace.")
    st.stop()

profile = load_profile(supa, user.id)
sub = subscription(supa, user.id)
projects = list_projects(supa, user.id)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Account", user.email or "Authenticated")
c2.metric("Plan", str(sub.get("plan", "free")).upper())
c3.metric("Projects", len(projects))
c4.metric("Cloud status", "Active")

with st.expander("➕ Create a cloud project", expanded=not projects):
    with st.form("cloud_create"):
        name = st.text_input("Project name", placeholder="H₂S biodegradation study")
        status = st.selectbox("Status", ["Planning", "Active", "Analysis", "Manuscript"])
        objective = st.text_area("Research objective", height=100)
        create = st.form_submit_button("Create project", type="primary")
    if create:
        if not name.strip():
            st.error("Enter a project name.")
        else:
            try:
                create_project(supa, user.id, name.strip(), status, objective.strip())
                st.success("Project created in Supabase.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not create project: {exc}")

if not projects:
    st.info("Create a project to unlock the persistent research workspace.")
    st.stop()

labels = {p["id"]: p["name"] for p in projects}
selected = st.selectbox("Active cloud project", [p["id"] for p in projects], format_func=lambda x: labels[x])
project = next(p for p in projects if p["id"] == selected)

datasets = list_project_datasets(supa, selected)
experiments = list_experiments(supa, selected)
milestones = list_milestones(supa, selected)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Datasets", len(datasets))
m2.metric("Experiments", len(experiments))
m3.metric("Milestones", len(milestones))
m4.metric("Completed", sum(bool(x.get("completed")) for x in milestones))

st.divider()
tabs = st.tabs(["📋 Overview", "📂 Datasets & Files", "🧪 Experiments", "📅 Milestones", "👤 Profile"])

with tabs[0]:
    st.subheader(project.get("name", "Cloud project"))
    with st.form("cloud_edit"):
        name = st.text_input("Name", project.get("name", ""))
        status_options = ["Planning", "Active", "Analysis", "Manuscript", "Completed"]
        current_status = project.get("status", "Planning")
        status = st.selectbox("Status", status_options, index=status_options.index(current_status) if current_status in status_options else 0)
        objective = st.text_area("Research objective", project.get("objective", ""), height=130)
        notes = st.text_area("Project notes", project.get("notes", ""), height=180)
        save = st.form_submit_button("💾 Save project")
    if save:
        try:
            save_project(supa, {"id": project["id"], "name": name.strip() or project["name"], "status": status, "objective": objective, "notes": notes})
            st.success("Project updated in the cloud.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not save project: {exc}")

with tabs[1]:
    st.subheader("📂 Private research files")
    st.caption("Files are stored in the private `research-files` bucket under your authenticated project path. Database records keep metadata and the storage path.")
    with st.form("dataset_upload"):
        upload = st.file_uploader("Upload research dataset", type=["csv", "xlsx", "xls", "txt", "pdf", "png", "jpg", "jpeg", "zip"])
        upload_now = st.form_submit_button("☁️ Upload to private cloud storage", type="primary")
    if upload_now:
        if upload is None:
            st.error("Choose a file first.")
        else:
            try:
                raw = upload.getvalue()
                if len(raw) > 50 * 1024 * 1024:
                    raise ValueError("File exceeds the 50 MB application upload limit.")
                content_type = upload.type or "application/octet-stream"
                storage_path = upload_project_file(supa, user.id, selected, upload.name, raw, content_type)
                rows = cols = 0
                if upload.name.lower().endswith(".csv"):
                    df = pd.read_csv(pd.io.common.BytesIO(raw))
                    rows, cols = df.shape
                elif upload.name.lower().endswith((".xlsx", ".xls")):
                    df = pd.read_excel(pd.io.common.BytesIO(raw))
                    rows, cols = df.shape
                register_dataset(supa, user.id, selected, upload.name, storage_path, rows, cols)
                st.success(f"Uploaded **{upload.name}** to private cloud storage.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not upload file: {exc}")

    if datasets:
        st.dataframe(pd.DataFrame(datasets), width="stretch", hide_index=True)
        st.markdown("### Secure file access")
        for item in datasets:
            path = item.get("storage_path", "")
            if not path:
                continue
            a, b = st.columns([4, 1])
            a.write(f"**{item.get('name', 'File')}**  ·  {item.get('row_count', 0):,} rows × {item.get('column_count', 0):,} columns")
            try:
                signed = create_download_url(supa, path, 3600)
                if signed:
                    b.link_button("Open / download", signed)
                else:
                    b.caption("URL unavailable")
            except Exception:
                b.caption("Access unavailable")
    else:
        st.info("No cloud files registered for this project yet.")

with tabs[2]:
    st.subheader("Experiment registry")
    with st.form("experiment_form"):
        exp_name = st.text_input("Experiment name")
        design = st.text_input("Design / comparison")
        outcome = st.text_input("Primary outcome")
        exp_status = st.selectbox("Status", ["Planned", "Running", "Analysing", "Complete"])
        add_exp = st.form_submit_button("➕ Add experiment")
    if add_exp:
        if not exp_name.strip():
            st.error("Enter an experiment name.")
        else:
            try:
                create_experiment(supa, user.id, selected, exp_name.strip(), design.strip(), outcome.strip(), exp_status)
                st.success("Experiment saved to the cloud.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save experiment: {exc}")
    if experiments:
        st.dataframe(pd.DataFrame(experiments), width="stretch", hide_index=True)
    else:
        st.info("No experiments registered yet.")

with tabs[3]:
    st.subheader("Project milestones")
    with st.form("milestone_form"):
        title = st.text_input("Milestone")
        due = st.date_input("Target date")
        add_m = st.form_submit_button("➕ Add milestone")
    if add_m:
        if not title.strip():
            st.error("Enter a milestone title.")
        else:
            try:
                create_milestone(supa, user.id, selected, title.strip(), due.isoformat())
                st.success("Milestone saved to the cloud.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save milestone: {exc}")
    for milestone in milestones:
        done = st.checkbox(f"{milestone.get('title', 'Milestone')} — {milestone.get('due_date') or 'No target date'}", value=bool(milestone.get("completed")), key=f"cloud_milestone_{milestone['id']}")
        if done != bool(milestone.get("completed")):
            try:
                set_milestone_completed(supa, milestone["id"], done)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not update milestone: {exc}")
    if not milestones:
        st.info("No milestones yet.")

with tabs[4]:
    st.subheader("Researcher profile")
    with st.form("profile"):
        full_name = st.text_input("Full name", profile.get("full_name", ""))
        institution = st.text_input("Institution / Lab", profile.get("institution", ""))
        save_profile_button = st.form_submit_button("💾 Save profile")
    if save_profile_button:
        try:
            save_profile(supa, user.id, full_name.strip(), institution.strip(), profile.get("avatar_url", ""))
            st.success("Profile saved.")
        except Exception as exc:
            st.error(f"Could not save profile: {exc}")

st.divider()
st.success("☁️ Persistent cloud project metadata and private file storage are ready when Supabase is configured.")
st.caption("Storage uses short-lived signed URLs rather than public file links. Raw research files remain separate from database metadata.")
