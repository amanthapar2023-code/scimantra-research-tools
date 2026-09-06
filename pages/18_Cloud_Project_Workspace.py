import pandas as pd
import streamlit as st

from src.scimantra.cloud import client, configured, current_user, create_project, list_projects, load_profile, save_profile, save_project, subscription

st.set_page_config(page_title="SciMantra Cloud Workspace", page_icon="☁️", layout="wide")
st.title("☁️ SciMantra Cloud Research Workspace")
st.caption("Persistent projects for authenticated researchers. Configure Supabase to activate cloud persistence.")

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

c1, c2, c3 = st.columns(3)
c1.metric("Account", user.email or "Authenticated")
c2.metric("Plan", str(sub.get("plan", "free")).upper())
c3.metric("Status", str(sub.get("status", "active")).title())

projects = list_projects(supa, user.id)

left, right = st.columns([2, 1])
with left:
    st.subheader("Your cloud projects")
    if projects:
        st.dataframe(pd.DataFrame(projects), width="stretch", hide_index=True)
    else:
        st.info("No cloud projects yet. Create your first project on the right.")

with right:
    st.subheader("Create project")
    with st.form("cloud_create"):
        name = st.text_input("Project name", placeholder="H₂S biodegradation study")
        status = st.selectbox("Status", ["Planning", "Active", "Analysis", "Manuscript"])
        objective = st.text_area("Objective", height=120)
        create = st.form_submit_button("➕ Create", type="primary")
    if create:
        if not name.strip():
            st.error("Enter a project name.")
        else:
            try:
                create_project(supa, user.id, name.strip(), status, objective.strip())
                st.success("Project saved to the cloud.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not create project: {exc}")

if projects:
    st.divider()
    labels = {p["id"]: p["name"] for p in projects}
    selected = st.selectbox("Active project", [p["id"] for p in projects], format_func=lambda x: labels[x])
    project = next(p for p in projects if p["id"] == selected)

    with st.form("cloud_edit"):
        name = st.text_input("Name", project.get("name", ""))
        status_options = ["Planning", "Active", "Analysis", "Manuscript", "Completed"]
        current_status = project.get("status", "Planning")
        status = st.selectbox("Status", status_options, index=status_options.index(current_status) if current_status in status_options else 0)
        objective = st.text_area("Research objective", project.get("objective", ""), height=150)
        notes = st.text_area("Project notes", project.get("notes", ""), height=220)
        save = st.form_submit_button("💾 Save to cloud")
    if save:
        try:
            save_project(supa, {"id": project["id"], "name": name.strip() or project["name"], "status": status, "objective": objective, "notes": notes})
            st.success("Project updated in the cloud.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not save project: {exc}")

st.divider()
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

st.success("☁️ Cloud persistence is active for this authenticated session.")
st.caption("Dataset files should be stored in a private object-storage bucket in production; the database keeps metadata and storage paths rather than raw file bytes.")
