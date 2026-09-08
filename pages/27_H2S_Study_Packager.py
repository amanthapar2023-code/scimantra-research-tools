from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

try:
    from src.scimantra.research_session import get_dataframe, metadata
except Exception:
    get_dataframe = lambda: None
    metadata = lambda: {}

st.set_page_config(page_title="H₂S Study Packager", page_icon="🗂️", layout="wide")
st.title("🗂️ H₂S Complete Study Packager")
st.caption("Create one reproducible ZIP package containing the dataset, analysis manifest, manuscript materials, and submission evidence.")

st.markdown("### 1. Study identity")
col1, col2 = st.columns(2)
with col1:
    study_title = st.text_input("Study title", "H₂S bioreactor treatment performance study")
    project_id = st.text_input("Project / study ID", "H2S-STUDY-001")
    researcher = st.text_input("Researcher / laboratory", "")
with col2:
    journal = st.text_input("Target journal (optional)", "")
    version = st.text_input("Package version", "1.0")
    notes = st.text_area("Package notes", "", height=100)

st.markdown("### 2. Dataset")
current_df = get_dataframe()
current_meta = metadata()
source_name = current_meta.get("filename", "Current Data Analyzer dataset") if isinstance(current_meta, dict) else "Current Data Analyzer dataset"

uploaded = st.file_uploader("Upload the study dataset if it is not already in the Data Analyzer", type=["csv", "xlsx", "xls"])
df = None
if uploaded is not None:
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            sheets = pd.read_excel(uploaded, sheet_name=None)
            numeric_counts = {name: s.select_dtypes(include="number").shape[0] * s.select_dtypes(include="number").shape[1] for name, s in sheets.items()}
            chosen = max(numeric_counts, key=numeric_counts.get) if numeric_counts else next(iter(sheets))
            df = sheets[chosen]
            source_name = f"{uploaded.name} | {chosen}"
    except Exception as exc:
        st.error(f"Could not read the uploaded dataset: {exc}")
elif current_df is not None and not current_df.empty:
    df = current_df.copy()

if df is None or df.empty:
    st.info("Upload a dataset or load one through Data Analyzer to generate a study package.")
    st.stop()

st.success(f"Dataset ready: {source_name} · {df.shape[0]} rows × {df.shape[1]} columns")

st.markdown("### 3. Package contents")
contents = {
    "Raw/processed dataset CSV": st.checkbox("Include dataset", True),
    "Dataset metadata": st.checkbox("Include dataset metadata", True),
    "Analysis manifest": st.checkbox("Include analysis manifest", True),
    "Methods template": st.checkbox("Include methods template", True),
    "Results template": st.checkbox("Include results template", True),
    "Figure plan": st.checkbox("Include publication figure plan", True),
    "Reproducibility checklist": st.checkbox("Include reproducibility checklist", True),
    "Submission checklist": st.checkbox("Include journal submission checklist", True),
}

st.markdown("### 4. Analysis configuration")
cols = list(df.columns)
def pick(label: str, options: list[str], keywords: list[str]) -> str:
    if not options:
        return ""
    for c in options:
        if any(k in str(c).lower() for k in keywords):
            return c
    return options[0]

numeric = df.select_dtypes(include="number").columns.tolist()
inlet = st.selectbox("Inlet H₂S column", ["(not selected)"] + numeric, index=0)
outlet = st.selectbox("Outlet H₂S column", ["(not selected)"] + numeric, index=0)
group_options = ["(not selected)"] + cols
group = st.selectbox("Experimental group / treatment", group_options, index=0)
replicate = st.selectbox("Replicate ID", group_options, index=0)
time_col = st.selectbox("Time column", group_options, index=0)
units = st.text_input("H₂S units", "ppm")

analysis = df.copy()
if inlet != "(not selected)" and outlet != "(not selected)":
    analysis["H2S_Removal_Percent"] = ((analysis[inlet] - analysis[outlet]) / analysis[inlet].replace(0, pd.NA) * 100)
    valid = analysis["H2S_Removal_Percent"].dropna()
    st.metric("Valid H₂S observations", int(valid.shape[0]))
    if not valid.empty:
        st.metric("Mean removal", f"{valid.mean():.2f}%")
        st.metric("SD", f"{valid.std(ddof=1):.2f}%" if len(valid) > 1 else "—")
else:
    st.info("Select inlet and outlet H₂S columns to add calculated removal evidence.")

st.markdown("### 5. Package preview")
preview_cols = [c for c in [inlet, outlet, group, replicate, time_col, "H2S_Removal_Percent"] if c and c != "(not selected)" and c in analysis.columns]
st.dataframe(analysis[preview_cols].head(10) if preview_cols else analysis.head(10), width="stretch")

created = datetime.now(timezone.utc).isoformat()
manifest = {
    "package_version": version,
    "created_utc": created,
    "study": {"title": study_title, "project_id": project_id, "researcher": researcher, "target_journal": journal, "notes": notes},
    "source": {"name": source_name, "rows": int(df.shape[0]), "columns": int(df.shape[1]), "column_names": cols},
    "analysis": {"inlet_h2s": inlet, "outlet_h2s": outlet, "group": group, "replicate": replicate, "time": time_col, "units": units},
    "contents": contents,
    "scientific_safeguards": [
        "Preserve the original raw file separately from this generated package.",
        "Verify all calculations against the experimental record before submission.",
        "Do not treat row-level observations as independent biological replicates unless the experimental design supports that interpretation.",
        "Do not claim a validated optimum or causality without appropriate experimental confirmation.",
    ],
}

methods = f"""# Materials and Methods — working template\n\nStudy: {study_title}\n\nThe experimental dataset was analyzed using a documented computational workflow. H₂S measurements were expressed in {units}. Where inlet and outlet measurements were available, removal efficiency was calculated as:\n\nRemoval (%) = ((Inlet H₂S − Outlet H₂S) / Inlet H₂S) × 100\n\nSelected analysis fields:\n- Inlet H₂S: {inlet}\n- Outlet H₂S: {outlet}\n- Experimental group: {group}\n- Replicate ID: {replicate}\n- Time: {time_col}\n\nThe experimental unit, replication structure, inclusion/exclusion criteria, analytical assumptions, and statistical tests must be finalized from the actual study protocol before manuscript submission.\n"""

results = """# Results — working template\n\nThe study dataset contained {rows} rows and {columns} columns. The quantitative H₂S analysis should report the number of valid observations, experimental replicates, treatment-specific estimates, uncertainty measures, and the statistical tests used.\n\nCalculated removal-efficiency results are included in the packaged dataset when inlet and outlet H₂S columns were selected. Replace this template with the verified manuscript Results text generated from the study evidence.\n""".format(rows=df.shape[0], columns=df.shape[1])

figure_plan = """# Publication Figure Plan\n\n1. Inlet versus outlet H₂S — show individual observations and appropriate summary statistics.\n2. H₂S removal by treatment/group — show replicate-level points and uncertainty.\n3. H₂S removal versus EBRT — only if EBRT is measured or calculated from the study data.\n4. H₂S removal versus loading — only if loading is defined from the experimental protocol.\n5. Time-course plot — only when time is an experimental variable.\n\nEvery figure should state units, n, experimental unit, and error-bar definition.\n"""

repro = """# Reproducibility Checklist\n\n- [ ] Original raw data preserved\n- [ ] Dataset version/fingerprint recorded\n- [ ] Measurement units documented\n- [ ] Experimental unit defined\n- [ ] Biological/technical replicate distinction documented\n- [ ] Inclusion/exclusion rules recorded\n- [ ] Calculation formulas recorded\n- [ ] Statistical assumptions assessed\n- [ ] Figure error bars defined\n- [ ] n values reported\n- [ ] Negative/zero/invalid measurements reviewed\n- [ ] Manuscript values checked against analysis output\n- [ ] Author and journal requirements verified\n"""

submission = """# Journal Submission Checklist\n\n- [ ] Manuscript complete\n- [ ] Figures numbered and cited\n- [ ] Tables numbered and cited\n- [ ] References verified\n- [ ] Data availability statement verified\n- [ ] Funding statement verified\n- [ ] Conflict-of-interest statement verified\n- [ ] Ethics/biosafety declarations verified\n- [ ] Cover letter finalized\n- [ ] Journal author instructions checked\n- [ ] All quantitative claims independently verified\n"""

if st.button("🗜️ Build complete study ZIP", type="primary", width="stretch"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("00_MANIFEST/study_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        if contents["Raw/processed dataset CSV"]:
            z.writestr("01_DATA/h2s_dataset.csv", analysis.to_csv(index=False))
        if contents["Dataset metadata"]:
            z.writestr("01_DATA/dataset_metadata.json", json.dumps({"source": source_name, "rows": int(df.shape[0]), "columns": int(df.shape[1]), "columns_list": cols}, indent=2, ensure_ascii=False))
        if contents["Analysis manifest"]:
            z.writestr("02_ANALYSIS/analysis_manifest.json", json.dumps(manifest["analysis"], indent=2, ensure_ascii=False))
        if contents["Methods template"]:
            z.writestr("03_MANUSCRIPT/methods_working_template.md", methods)
        if contents["Results template"]:
            z.writestr("03_MANUSCRIPT/results_working_template.md", results)
        if contents["Figure plan"]:
            z.writestr("04_FIGURES/publication_figure_plan.md", figure_plan)
        if contents["Reproducibility checklist"]:
            z.writestr("05_REPRODUCIBILITY/reproducibility_checklist.md", repro)
        if contents["Submission checklist"]:
            z.writestr("06_SUBMISSION/journal_submission_checklist.md", submission)
        z.writestr("README.md", f"# {study_title}\n\nGenerated: {created}\nProject ID: {project_id}\n\nThis package is a structured working evidence bundle. Preserve the original raw data and verify all scientific conclusions before publication.\n")
    buffer.seek(0)
    st.success("Complete study package built successfully.")
    st.download_button("⬇️ Download complete H₂S study package (.zip)", buffer.getvalue(), "h2s_complete_study_package.zip", "application/zip", width="stretch")

st.warning("The ZIP is an evidence-organization package, not a certification of data quality, experimental validity, authorship, or journal compliance.")
