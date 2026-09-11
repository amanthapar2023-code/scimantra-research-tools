from __future__ import annotations
import hashlib
from datetime import datetime, timezone
import streamlit as st
from src.scimantra.cloud import client, configured, list_artifacts, create_artifact, delete_artifact, upload_project_file, create_download_url

st.title("🗄️ Research Artifact Vault")
st.caption("Persistent project storage for datasets, analyses, figures, reports, manuscripts, evidence and submission packages.")
supa=client(st.secrets) if configured(st.secrets) else None
user=None
if supa:
    try: user=supa.auth.get_user().user
    except Exception: pass
if not supa or not user:
    st.info("Connect and sign in to Supabase Cloud to use the persistent Artifact Vault.")
    st.stop()
projects=supa.table("projects").select("*").order("updated_at",desc=True).execute().data or []
if not projects: st.warning("Create a project in Cloud Project Workspace first."); st.stop()
by_name={p["name"]:p for p in projects}; name=st.selectbox("Research project",list(by_name)); project=by_name[name]
arts=list_artifacts(supa,project["id"])
c=st.columns(4); c[0].metric("Artifacts",len(arts)); c[1].metric("Figures",sum(a.get("artifact_type")=="figure" for a in arts)); c[2].metric("Reports",sum(a.get("artifact_type")=="report" for a in arts)); c[3].metric("Packages",sum(a.get("artifact_type")=="package" for a in arts))
with st.form("artifact_upload"):
    f=st.file_uploader("Research output",type=["csv","xlsx","txt","pdf","png","jpg","jpeg","svg","zip","md","json"]); typ=st.selectbox("Artifact type",["dataset","analysis","figure","report","manuscript","evidence","submission","package","other"]); tool=st.text_input("Source tool",placeholder="e.g. H₂S Figure Engine"); note=st.text_area("Provenance note"); save=st.form_submit_button("⬆️ Save to project",type="primary")
if save:
    if not f: st.error("Choose a file first.")
    else:
        data=f.getvalue(); digest=hashlib.sha256(data).hexdigest(); path=upload_project_file(supa,str(user.id),project["id"],"artifacts/"+f.name,data,f.type or "application/octet-stream")
        create_artifact(supa,str(user.id),project["id"],f.name,typ,path,f.type or "application/octet-stream",len(data),digest,tool,{"note":note,"uploaded_at":datetime.now(timezone.utc).isoformat()})
        st.success("Artifact saved."); st.rerun()
st.divider(); st.subheader("📚 Project artifacts")
if not arts: st.info("No artifacts stored yet.")
for a in arts:
    with st.container(border=True):
        cols=st.columns([2.4,1,1,1]); cols[0].markdown(f"**{a.get('name','')}**  \n\n`{a.get('artifact_type','other')}` • {a.get('source_tool') or 'Manual upload'}"); cols[1].caption(f"{(a.get('size_bytes',0) or 0)/1024:.1f} KB")
        url=create_download_url(supa,a.get("storage_path","")) if a.get("storage_path") else ""
        if url: cols[2].link_button("Open",url,width="stretch")
        if cols[3].button("Delete",key="del_"+a["id"],width="stretch"):
            delete_artifact(supa,a["id"]); st.rerun()
st.divider(); st.caption("🔐 Private project artifacts • SHA-256 fingerprinting • provenance metadata • no automatic alteration of research evidence.")
