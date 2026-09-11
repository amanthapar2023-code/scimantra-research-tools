import io
import mimetypes
import zipfile

import pandas as pd
import streamlit as st

from src.scimantra.cloud import (
    client, configured, create_download_url, current_user, delete_project_file,
    list_project_datasets, list_projects, register_dataset, upload_project_file,
)

st.set_page_config(page_title="SciMantra Research Artifact Vault", page_icon="🗄️", layout="wide")
st.title("🗄️ Research Artifact Vault")
st.caption("Keep datasets, figures, reports, manuscripts and reproducibility packages with the research project that produced them.")

if not configured(st.secrets):
    st.info("Cloud mode is not configured. Configure Supabase using supabase/schema.sql and the required Streamlit secrets to activate the vault.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa)
if user is None:
    st.warning("Please sign in from **👤 Login & Cloud Account** first.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("Create a cloud project first in **☁️ Cloud Research Workspace**.")
    st.stop()

labels = {p["id"]: p["name"] for p in projects}
selected = st.selectbox("Research project", [p["id"] for p in projects], format_func=lambda x: labels[x])

records = list_project_datasets(supa, selected)

c1, c2, c3 = st.columns(3)
c1.metric("Registered artifacts", len(records))
c2.metric("Datasets", sum(str(x.get("name", "")).lower().endswith((".csv", ".xlsx", ".xls")) for x in records))
c3.metric("Project", labels[selected])

st.divider()

left, right = st.columns([1.15, 1])
with left:
    st.subheader("⬆️ Add artifact")
    st.caption("Upload the output of any SciMantra analysis: raw data, cleaned datasets, figures, manuscripts, reports, evidence passports or ZIP research packages.")
    with st.form("artifact_upload"):
        artifact = st.file_uploader(
            "Choose a research artifact",
            type=["csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg", "svg", "zip", "docx", "txt", "md", "json"],
        )
        upload = st.form_submit_button("☁️ Save to project vault", type="primary")
    if upload:
        if artifact is None:
            st.error("Choose a file first.")
        else:
            raw = artifact.getvalue()
            if len(raw) > 100 * 1024 * 1024:
                st.error("Files larger than 100 MB are not accepted by this application layer.")
            else:
                try:
                    content_type = artifact.type or mimetypes.guess_type(artifact.name)[0] or "application/octet-stream"
                    path = upload_project_file(supa, user.id, selected, artifact.name, raw, content_type)
                    rows = cols = 0
                    lower = artifact.name.lower()
                    if lower.endswith(".csv"):
                        df = pd.read_csv(io.BytesIO(raw))
                        rows, cols = df.shape
                    elif lower.endswith((".xlsx", ".xls")):
                        df = pd.read_excel(io.BytesIO(raw))
                        rows, cols = df.shape
                    register_dataset(supa, user.id, selected, artifact.name, path, rows, cols)
                    st.success(f"Saved **{artifact.name}** to the private project vault.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save artifact: {exc}")

with right:
    st.subheader("📦 Package outputs")
    st.write("You can upload ZIP packages produced by the manuscript, reproducibility and submission tools. They remain a single versioned project artifact.")
    st.markdown("**Recommended project trail**")
    st.markdown("1. Raw dataset\n2. Quality audit\n3. Statistical validation\n4. Publication figures\n5. Manuscript/evidence files\n6. Reproducibility passport\n7. Submission package")

st.divider()
st.subheader("📚 Project artifact library")
if not records:
    st.info("No artifacts have been registered for this project yet.")
else:
    for item in records:
        name = item.get("name", "Artifact")
        path = item.get("storage_path", "")
        ext = name.rsplit(".", 1)[-1].upper() if "." in name else "FILE"
        a, b, c = st.columns([3.5, 1.5, 1])
        a.markdown(f"**{name}**  \n`{ext}` · {item.get('row_count', 0):,} rows × {item.get('column_count', 0):,} columns")
        if path:
            try:
                signed = create_download_url(supa, path, 1800)
                if signed:
                    b.link_button("Open", signed)
                else:
                    b.caption("Link unavailable")
            except Exception:
                b.caption("Access unavailable")
        if path and c.button("Delete", key=f"delete_{item['id']}"):
            try:
                delete_project_file(supa, path)
                supa.table("datasets").delete().eq("id", item["id"]).execute()
                st.success(f"Removed {name} from the project vault.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not remove artifact: {exc}")

st.divider()
st.warning("Scientific integrity rule: the vault stores artifacts; it does not silently alter, overwrite or manufacture research results. Keep the raw dataset and preserve reproducibility outputs alongside derived files.")
