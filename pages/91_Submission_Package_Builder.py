"""SciMantra Research OS — Submission Package Builder."""
import pandas as pd
import streamlit as st
from src.scimantra.submission_package_builder import ITEMS, audit, manifest

st.set_page_config(page_title="Submission Package Builder", page_icon="📦", layout="wide")
st.title("📦 Submission Package Builder")
st.caption("Assemble and audit the materials needed for a journal submission.")
st.warning("This creates a submission manifest and readiness checklist. It does not upload files to a journal or replace the target journal's current submission instructions.")

package={}
st.subheader("Submission package")
for i,(label,key,required) in enumerate(ITEMS):
    c1,c2,c3=st.columns([2,1,4])
    c1.write(f"**{label}**" + (" · required" if required else " · optional"))
    ready=c2.checkbox("Ready",key=f"pkg_ready_{i}")
    location=c3.text_input("Location",placeholder="filename / folder / URL",key=f"pkg_loc_{i}",label_visibility="collapsed")
    package[key]={"ready":ready,"location":location}

result=audit(package)
a,b,c=st.columns(3)
a.metric("Required ready",f'{result["ready_required"]}/{result["required"]}')
b.metric("Required missing",len(result["missing"]))
c.metric("Package status","READY" if result["ready"] else "INCOMPLETE")

if result["ready"]: st.success("All required package components are marked ready.")
else:
    st.error("Submission package is incomplete.")
    for item in result["missing"]: st.write("→ Missing:",item)

st.divider(); st.subheader("Submission manifest")
df=pd.DataFrame(manifest(package)); st.dataframe(df,use_container_width=True,hide_index=True)
st.download_button("Download submission manifest CSV",df.to_csv(index=False),"scimantra_submission_manifest.csv","text/csv")

st.info("Before submission: verify file names, formats, figure resolution, declarations, reference style, supplementary limits, and the journal's latest author instructions.")
st.caption("Module 91 · Submission package organization layer.")
