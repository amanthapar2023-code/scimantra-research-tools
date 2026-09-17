"""SciMantra V1.1 Data Integrity Gate.

A deterministic pre-analysis gate that reports whether a dataset has basic
integrity risks. It never modifies or deletes the source data.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st

st.title("🛡️ V1.1 Data Integrity Gate")
st.caption("Deterministic pre-analysis checks for dataset structure, missingness, duplicates and experimental-unit consistency.")

df = st.session_state.get("scimantra_research_df")
if df is None:
    upload = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])
    if upload is not None:
        try:
            df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
        except Exception as exc:
            st.error(f"Could not read dataset: {exc}")
            st.stop()
if df is None or df.empty:
    st.info("Load a dataset in Data Analyzer or upload one here.")
    st.stop()

df = df.copy()
raw_bytes = df.to_csv(index=False).encode("utf-8")
fingerprint = hashlib.sha256(raw_bytes).hexdigest()

st.success(f"Dataset loaded: **{len(df):,} rows × {len(df.columns):,} columns**")
c = st.columns(5)
c[0].metric("Rows", f"{len(df):,}")
c[1].metric("Columns", f"{len(df.columns):,}")
c[2].metric("Missing", f"{int(df.isna().sum().sum()):,}")
c[3].metric("Duplicates", f"{int(df.duplicated().sum()):,}")
c[4].metric("Fingerprint", fingerprint[:12] + "…")

checks: list[dict] = []
def check(name: str, passed: bool, detail: str):
    checks.append({"check": name, "status": "PASS" if passed else "REVIEW", "detail": detail})

check("Dataset non-empty", not df.empty, "At least one row is present.")
check("Column names unique", not df.columns.duplicated().any(), "Duplicate column names must be resolved before unambiguous analysis." if df.columns.duplicated().any() else "All column names are unique.")
missing = int(df.isna().sum().sum())
check("Missingness reviewed", missing == 0, f"{missing:,} missing cells detected; inspect field-level missingness before inference.")
dups = int(df.duplicated().sum())
check("Duplicate rows reviewed", dups == 0, f"{dups:,} exact duplicate rows detected; determine whether they are legitimate repeated observations.")
unnamed = [str(x) for x in df.columns if str(x).lower().startswith("unnamed:")]
check("Index-like columns reviewed", len(unnamed) == 0, f"{len(unnamed)} index-like column(s) detected." if unnamed else "No Unnamed:index-like columns detected.")
constant = [str(x) for x in df.columns if df[x].nunique(dropna=True) <= 1]
check("Constant fields reviewed", len(constant) == 0, f"{len(constant)} field(s) have no observed variation." if constant else "No constant fields detected.")

st.subheader("Integrity results")
st.dataframe(pd.DataFrame(checks), width="stretch", hide_index=True)

st.subheader("Experimental-unit consistency")
categorical = [x for x in df.columns if not pd.api.types.is_numeric_dtype(df[x])]
if categorical:
    group = st.selectbox("Treatment / group", ["—"] + categorical)
    replicate = st.selectbox("Experimental unit / replicate", ["—"] + categorical)
    if group != "—" and replicate != "—":
        temp = df[[group, replicate]].dropna()
        balance = temp.groupby(group)[replicate].nunique().reset_index(name="experimental_units")
        repeated = temp.groupby([group, replicate]).size().reset_index(name="observations")
        balance["min_obs_per_unit"] = repeated.groupby(group)["observations"].min().reindex(balance[group]).to_numpy()
        balance["max_obs_per_unit"] = repeated.groupby(group)["observations"].max().reindex(balance[group]).to_numpy()
        st.dataframe(balance, width="stretch", hide_index=True)
        uneven = len(balance) > 1 and balance["experimental_units"].nunique() > 1
        check("Replicate structure reviewed", not uneven, "Unequal unit counts across groups require explicit design consideration." if uneven else "Experimental-unit counts are balanced across groups.")

st.subheader("Gate decision")
review_count = sum(x["status"] == "REVIEW" for x in checks)
if review_count == 0:
    st.success("🟢 DATA INTEGRITY GATE: PASS")
    decision = "PASS"
else:
    st.warning(f"🟠 DATA INTEGRITY GATE: REVIEW REQUIRED — {review_count} check(s) need inspection.")
    decision = "REVIEW REQUIRED"
st.caption("A REVIEW flag does not mean the dataset is wrong. It means the researcher must document how the issue is handled.")

manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "rows": len(df), "columns": len(df.columns), "sha256": fingerprint,
    "decision": decision, "checks": checks,
}
st.download_button("Download integrity manifest (JSON)", json.dumps(manifest, indent=2, default=str).encode(), "scimantra_v1_1_integrity_manifest.json", "application/json")
st.info("Scientific safeguard: this gate is diagnostic only. It never deletes, imputes, excludes or silently transforms source observations.")
