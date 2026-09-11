from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file
from src.scimantra.research_session import get_dataframe, metadata

st.title("🧾 H₂S Reproducibility & Evidence Passport")

def save_passport_to_vault(payload, json_bytes, workbook_bytes, md_bytes):
    supa = client(st.secrets) if configured(st.secrets) else None
    if not supa:
        st.info("Connect Supabase Cloud to save this passport to a project.")
        return
    try:
        user = supa.auth.get_user().user
        projects = supa.table("projects").select("id,name").order("updated_at", desc=True).execute().data or []
        if not projects:
            st.warning("Create a Cloud Research Project first.")
            return
        names = {x["name"]: x["id"] for x in projects}
        project_name = st.selectbox("Vault project", list(names), key="passport_vault_project")
        if st.button("☁️ Save Passport to Project Vault", type="primary", key="save_passport_vault"):
            for fname, data, typ, ctype in [
                ("h2s_evidence_passport.json", json_bytes, "evidence", "application/json"),
                ("h2s_evidence_passport.xlsx", workbook_bytes, "evidence", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("h2s_evidence_passport.md", md_bytes, "evidence", "text/markdown")]:
                digest = hashlib.sha256(data).hexdigest()
                path = upload_project_file(supa, str(user.id), names[project_name], fname, data, ctype)
                create_artifact(supa, str(user.id), names[project_name], fname, typ, path, ctype, len(data), digest, "H₂S Reproducibility & Evidence Passport", {"dataset_sha256": payload.get("dataset_sha256"), "passport_version": payload.get("passport_version"), "source": payload.get("source")})
            st.success("Evidence Passport saved to the project Vault.")
    except Exception as exc:
        st.error(f"Vault save failed: {exc}")

st.caption("A machine-readable audit trail connecting a dataset to its calculations, analysis decisions, statistics and manuscript-ready evidence.")


def numeric(s):
    return pd.to_numeric(s, errors="coerce")


def detect(df, terms):
    return [c for c in df.columns if any(t in str(c).lower().replace("₂", "2") for t in terms)]


def workbook(payload, analysis, summary):
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        analysis.to_excel(w, index=False, sheet_name="Analysis")
        summary.to_excel(w, index=False, sheet_name="Evidence_Summary")
        pd.DataFrame([payload]).to_excel(w, index=False, sheet_name="Passport")
    return b.getvalue()


df = get_dataframe()
if df is None:
    up = st.file_uploader("Upload the dataset", type=["xlsx", "csv"])
    if not up:
        st.info("Select an H₂S worksheet in Data Analyzer first, or upload a dataset here.")
        st.stop()
    if up.name.lower().endswith(".csv"):
        df = pd.read_csv(up); source = up.name
    else:
        x = pd.ExcelFile(up)
        sheet = st.selectbox("Worksheet", x.sheet_names)
        df = pd.read_excel(x, sheet_name=sheet); source = f"{up.name} • {sheet}"
else:
    m = metadata(); source = m.get("filename", "current dataset") + (f" • {m['sheet']}" if m.get("sheet") else "")
    st.success(f"Using current Data Analyzer dataset: **{source}**")

# Stable fingerprint of the analyzed table, independent of Streamlit session state.
canonical = df.copy().fillna("<NA>").astype(str).to_csv(index=False).encode("utf-8")
fingerprint = hashlib.sha256(canonical).hexdigest()

h2s = detect(df, ["h2s", "hydrogen sulfide", "sulfide", "sulphide"])
inlet = detect(df, ["inlet", "influent", "input", "initial"])
outlet = detect(df, ["outlet", "effluent", "output", "final"])
groups = detect(df, ["treatment", "reactor", "condition", "group"])
reps = detect(df, ["replicate", "biological replicate", "technical replicate", "rep"])
times = detect(df, ["time", "hour", "hr", "day", "minute", "min"])

if not h2s:
    st.error("No H₂S-related measurement columns were detected.")
    st.stop()

st.markdown("### 1. Analysis identity")
a = st.selectbox("Inlet H₂S column", inlet or h2s)
b_choices = [c for c in (outlet or h2s) if c != a] or h2s
b = st.selectbox("Outlet H₂S column", b_choices)
g = st.selectbox("Experimental group", ["None"] + groups)
r = st.selectbox("Replicate ID", ["None"] + reps)
t = st.selectbox("Time / run variable", ["None"] + times)
units = st.text_input("H₂S units", "")
notes = st.text_area("Researcher decision notes", "")

analysis = pd.DataFrame({"Inlet H₂S": numeric(df[a]), "Outlet H₂S": numeric(df[b])})
if g != "None": analysis["Group"] = df[g]
if r != "None": analysis["Replicate"] = df[r]
if t != "None": analysis["Time"] = df[t]
analysis = analysis.replace([np.inf, -np.inf], np.nan).dropna(subset=["Inlet H₂S", "Outlet H₂S"])
invalid_zero = int((analysis["Inlet H₂S"] == 0).sum())
analysis = analysis[analysis["Inlet H₂S"] != 0].copy()
analysis["Removal %"] = (analysis["Inlet H₂S"] - analysis["Outlet H₂S"]) / analysis["Inlet H₂S"] * 100
negative_n = int((analysis["Removal %"] < 0).sum())

# Explicit replicate-level aggregation, when an ID is supplied.
if "Replicate" in analysis:
    keys = [c for c in ["Group", "Replicate", "Time"] if c in analysis]
    evidence = analysis.groupby(keys, dropna=False)[["Inlet H₂S", "Outlet H₂S", "Removal %"]].mean().reset_index()
    aggregation = "Mean within Group × Replicate × Time"
else:
    evidence = analysis.copy()
    aggregation = "No aggregation; row-level analysis units"

n = len(evidence)
mean = float(evidence["Removal %"].mean()) if n else np.nan
sd = float(evidence["Removal %"].std(ddof=1)) if n > 1 else np.nan
sem = sd / np.sqrt(n) if n > 1 and np.isfinite(sd) else np.nan
ci = float(stats.t.ppf(.975, n - 1) * sem) if n > 1 and np.isfinite(sem) else np.nan

if "Group" in evidence:
    summary = evidence.groupby("Group")["Removal %"].agg(N="count", Mean="mean", SD="std", Median="median", Min="min", Max="max").reset_index()
    summary["SEM"] = summary["SD"] / np.sqrt(summary["N"])
else:
    summary = pd.DataFrame()

if not summary.empty and len(summary) >= 2:
    arrays = [evidence.loc[evidence["Group"] == x, "Removal %"].dropna().to_numpy() for x in summary["Group"]]
    if len(arrays) == 2:
        test = stats.ttest_ind(arrays[0], arrays[1], equal_var=False)
        test_name, stat_name, stat, p = "Welch t-test", "t", float(test.statistic), float(test.pvalue)
    else:
        test = stats.f_oneway(*arrays)
        test_name, stat_name, stat, p = "One-way ANOVA", "F", float(test.statistic), float(test.pvalue)
else:
    test_name = stat_name = "Not run"; stat = p = np.nan

run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
payload = {
    "passport_version": "1.0",
    "created_utc": run_id,
    "source": source,
    "dataset_sha256": fingerprint,
    "source_rows": int(len(df)),
    "source_columns": int(len(df.columns)),
    "inlet_column": a,
    "outlet_column": b,
    "group_column": g,
    "replicate_column": r,
    "time_column": t,
    "h2s_units": units,
    "valid_analysis_units": n,
    "zero_inlet_excluded": invalid_zero,
    "negative_removal_observations": negative_n,
    "aggregation_rule": aggregation,
    "removal_formula": "((Inlet H2S - Outlet H2S) / Inlet H2S) * 100",
    "mean_removal_percent": mean,
    "sd_removal_percent": sd,
    "sem_removal_percent": sem,
    "ci95_half_width": ci,
    "statistical_test": test_name,
    "test_statistic": stat,
    "p_value": p,
    "researcher_notes": notes,
}

st.markdown("### 2. Evidence health check")
checks = [
    ("Dataset fingerprint", bool(fingerprint), fingerprint[:16] + "…"),
    ("Paired H₂S observations", n > 0, f"{n} valid units"),
    ("Replicate structure", r != "None", "Declared" if r != "None" else "Not supplied"),
    ("Zero inlet values", invalid_zero == 0, f"{invalid_zero} excluded"),
    ("Negative removal", negative_n == 0, f"{negative_n} observations"),
    ("Statistical comparison", not pd.isna(p), test_name),
]
for label, ok, detail in checks:
    st.write(("✅" if ok else "⚠️") + f" **{label}:** {detail}")

st.markdown("### 3. Reproducibility record")
cols = st.columns(4)
cols[0].metric("Dataset SHA-256", fingerprint[:12] + "…")
cols[1].metric("Source rows", len(df))
cols[2].metric("Evidence units", n)
cols[3].metric("Mean removal", f"{mean:.2f}%" if np.isfinite(mean) else "—")

st.json(payload)

st.markdown("### 4. Evidence tables")
st.dataframe(evidence.round(5), width="stretch", hide_index=True)
if not summary.empty:
    st.dataframe(summary.round(5), width="stretch", hide_index=True)

st.markdown("### 5. Machine-readable passport")
json_bytes = json.dumps({"passport": payload, "group_summary": summary.to_dict(orient="records"), "evidence_rows": evidence.to_dict(orient="records")}, indent=2, default=str).encode("utf-8")
md = "# H₂S Reproducibility & Evidence Passport\n\n" + "\n".join(f"- **{k}:** {v}" for k, v in payload.items())
col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("⬇️ Passport JSON", json_bytes, "h2s_evidence_passport.json", "application/json", width="stretch")
with col2:
    st.download_button("⬇️ Evidence workbook", workbook(payload, evidence, summary), "h2s_evidence_passport.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
with col3:
    st.download_button("⬇️ Audit record", md.encode("utf-8"), "h2s_evidence_passport.md", "text/markdown", width="stretch")

st.info("The SHA-256 fingerprint identifies the exact table representation analyzed in this session. It does not prove data authenticity; preserve the original raw file and laboratory metadata alongside this passport.")
