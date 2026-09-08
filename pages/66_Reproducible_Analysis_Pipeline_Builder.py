import pandas as pd
import streamlit as st
from scimantra.reproducible_pipeline import audit_pipeline, default_steps, dependency_map, export_pipeline

st.set_page_config(page_title="Reproducible Analysis Pipeline | SciMantra", layout="wide")
st.title("Reproducible Analysis Pipeline Builder")
st.caption("Record exactly how raw evidence becomes a reported scientific conclusion.")
st.warning("Integrity rule: this records and audits researcher-defined steps. It does not certify reproducibility unless the underlying files, code, versions, and execution are actually available.")

steps = st.session_state.get("repro_pipeline_steps")
if steps is None:
    steps = default_steps()
    st.session_state["repro_pipeline_steps"] = steps

st.subheader("1. Build the analysis chain")
for i, step in enumerate(steps):
    with st.expander(f"{step['ID']} — {step['Name']} ({step['Type']})", expanded=i < 2):
        c1, c2 = st.columns(2)
        step["Name"] = c1.text_input("Step name", step["Name"], key=f"name_{i}")
        step["Status"] = c2.selectbox("Status", ["Planned", "In progress", "Completed", "Not applicable"], index=["Planned", "In progress", "Completed", "Not applicable"].index(step["Status"]), key=f"status_{i}")
        c1, c2 = st.columns(2)
        step["owner"] = c1.text_input("Owner", step["owner"], key=f"owner_{i}")
        step["software"] = c2.text_input("Software / tool", step["software"], key=f"software_{i}")
        c1, c2 = st.columns(2)
        step["input"] = c1.text_input("Input artifact", step["input"], key=f"input_{i}")
        step["output"] = c2.text_input("Output artifact", step["output"], key=f"output_{i}")
        step["version"] = st.text_input("Version / commit / protocol revision", step["version"], key=f"version_{i}")
        step["rule"] = st.text_area("Exact rule / decision logic", step["rule"], key=f"rule_{i}")
        step["notes"] = st.text_area("Notes / provenance", step["notes"], key=f"notes_{i}")

result = audit_pipeline(steps)

st.subheader("2. Reproducibility audit")
a, b, c = st.columns(3)
a.metric("Pipeline stages", result["steps"])
b.metric("Documentation coverage", f"{result['coverage']}%")
c.metric("Audit status", "Ready" if result["complete"] else "Needs work")

if result["issues"]:
    st.error("Documentation gaps detected")
    for issue in result["issues"]:
        st.write(f"• {issue}")
else:
    st.success("All required pipeline fields are documented.")

st.subheader("3. Dependency chain")
st.dataframe(pd.DataFrame(dependency_map(steps)), use_container_width=True, hide_index=True)

st.subheader("4. Exportable analysis record")
st.download_button("Download pipeline record (Markdown)", export_pipeline(steps, result), "scimantra_reproducible_analysis_pipeline.md", "text/markdown", use_container_width=True)
