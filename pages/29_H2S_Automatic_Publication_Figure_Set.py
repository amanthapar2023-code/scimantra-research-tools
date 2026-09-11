from __future__ import annotations

import io
import zipfile
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.scimantra.research_session import get_dataframe
from src.scimantra.cloud import client, configured, create_artifact, upload_project_file


st.title("📚 H₂S Automatic Publication Figure Set")
st.caption("Generate a consistent six-figure evidence set from the active research dataset.")

active = get_dataframe()
upload = st.file_uploader("Upload dataset (CSV/XLS/XLSX)", type=["csv", "xls", "xlsx"])

def load_upload(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    if file.name.lower().endswith(".xls"):
        return pd.read_excel(file)
    return pd.read_excel(file)

if upload is not None:
    df = load_upload(upload)
    source = upload.name
elif active is not None:
    df = active.copy()
    source = "Current Data Analyzer dataset"
else:
    st.info("Upload a dataset or load one through Data Analyzer first.")
    st.stop()

st.success(f"Dataset loaded: {source} — {len(df):,} rows × {len(df.columns):,} columns")

cols = list(df.columns)
def find_col(words):
    for c in cols:
        s = str(c).lower()
        if any(w in s for w in words):
            return c
    return cols[0] if cols else None

inlet_default = find_col(["inlet", "influent", "input", "initial"])
outlet_default = find_col(["outlet", "effluent", "output", "final"])
group_default = find_col(["group", "treatment", "condition", "reactor"])
time_default = find_col(["time", "hour", "day"])
ebrt_default = find_col(["ebrt", "empty bed"])
loading_default = find_col(["loading", "load"])
ph_default = find_col(["ph"])

st.subheader("1. Configure evidence fields")
a, b, c = st.columns(3)
with a:
    inlet = st.selectbox("Inlet H₂S", ["—"] + cols, index=(cols.index(inlet_default)+1 if inlet_default in cols else 0))
    outlet = st.selectbox("Outlet H₂S", ["—"] + cols, index=(cols.index(outlet_default)+1 if outlet_default in cols else 0))
with b:
    group = st.selectbox("Treatment / group", ["—"] + cols, index=(cols.index(group_default)+1 if group_default in cols else 0))
    time_col = st.selectbox("Time", ["—"] + cols, index=(cols.index(time_default)+1 if time_default in cols else 0))
with c:
    ebrt = st.selectbox("EBRT", ["—"] + cols, index=(cols.index(ebrt_default)+1 if ebrt_default in cols else 0))
    loading = st.selectbox("Loading", ["—"] + cols, index=(cols.index(loading_default)+1 if loading_default in cols else 0))
ph = st.selectbox("pH", ["—"] + cols, index=(cols.index(ph_default)+1 if ph_default in cols else 0))

units = st.text_input("H₂S units", value="ppm")
error_bar = st.selectbox("Summary error bars", ["95% CI", "SEM", "SD"])
dpi = st.selectbox("Export resolution", [300, 600, 1200], index=1)
include_points = st.checkbox("Show individual observations", value=True)

work = df.copy()
if inlet != "—" and outlet != "—":
    work["Removal_%"] = np.where(
        pd.to_numeric(work[inlet], errors="coerce") != 0,
        (pd.to_numeric(work[inlet], errors="coerce") - pd.to_numeric(work[outlet], errors="coerce"))
        / pd.to_numeric(work[inlet], errors="coerce") * 100,
        np.nan,
    )

figures = []
metadata = []

def save_fig(fig, name, caption):
    png = io.BytesIO()
    svg = io.BytesIO()
    fig.savefig(png, format="png", dpi=dpi, bbox_inches="tight")
    fig.savefig(svg, format="svg", bbox_inches="tight")
    png.seek(0); svg.seek(0)
    figures.append((name + ".png", png.getvalue()))
    figures.append((name + ".svg", svg.getvalue()))
    metadata.append((name, caption))
    plt.close(fig)


def error_value(values, mode):
    x = pd.to_numeric(values, errors="coerce").dropna()
    if len(x) < 2:
        return 0.0
    if mode == "SD":
        return float(x.std(ddof=1))
    if mode == "SEM":
        return float(x.std(ddof=1) / np.sqrt(len(x)))
    return float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))

if inlet != "—" and outlet != "—":
    x = pd.to_numeric(work[inlet], errors="coerce")
    y = pd.to_numeric(work[outlet], errors="coerce")
    ok = x.notna() & y.notna()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x[ok], y[ok], alpha=0.75)
    lo = float(min(x[ok].min(), y[ok].min())) if ok.any() else 0
    hi = float(max(x[ok].max(), y[ok].max())) if ok.any() else 1
    ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)
    ax.set_xlabel(f"Inlet H₂S ({units})"); ax.set_ylabel(f"Outlet H₂S ({units})")
    ax.set_title("Figure 1. Inlet versus outlet H₂S")
    save_fig(fig, "Figure_1_Inlet_vs_Outlet_H2S", f"Inlet versus outlet H₂S concentrations ({units}); dashed line indicates equality.")

if "Removal_%" in work.columns:
    if group != "—":
        tmp = work[[group, "Removal_%"]].dropna()
        groups = list(tmp[group].astype(str).unique())
        vals = [tmp.loc[tmp[group].astype(str) == g, "Removal_%"].to_numpy() for g in groups]
        if vals:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.boxplot(vals, labels=groups, showmeans=True)
            if include_points:
                rng = np.random.default_rng(42)
                for i, v in enumerate(vals, 1):
                    ax.scatter(i + rng.uniform(-0.06, 0.06, len(v)), v, alpha=0.55)
            ax.set_ylabel("H₂S removal (%)"); ax.set_title("Figure 2. H₂S removal by treatment")
            save_fig(fig, "Figure_2_Removal_by_Treatment", "H₂S removal efficiency by treatment/group; points show individual observations where enabled.")
    else:
        vals = work["Removal_%"].dropna()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.bar(["Study"], [vals.mean()], yerr=[error_value(vals, error_bar)], capsize=5)
        ax.set_ylabel("H₂S removal (%)"); ax.set_title("Figure 2. Study-level H₂S removal")
        save_fig(fig, "Figure_2_Study_Removal", "Study-level H₂S removal efficiency with the selected uncertainty measure.")

    relationships = [("EBRT", ebrt, "Figure_3_Removal_vs_EBRT", "Removal (%)", "EBRT", "Removal efficiency versus EBRT."),
                     ("Loading", loading, "Figure_4_Removal_vs_Loading", "Removal (%)", "Loading", "Removal efficiency versus H₂S loading."),
                     ("pH", ph, "Figure_5_Removal_vs_pH", "Removal (%)", "pH", "Removal efficiency versus pH.")]
    for _, xc, fname, ylabel, xlabel, caption in relationships:
        if xc != "—":
            xx = pd.to_numeric(work[xc], errors="coerce")
            yy = pd.to_numeric(work["Removal_%"], errors="coerce")
            ok = xx.notna() & yy.notna()
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.scatter(xx[ok], yy[ok], alpha=0.75)
            if ok.sum() >= 3:
                z = np.polyfit(xx[ok], yy[ok], 1)
                grid = np.linspace(xx[ok].min(), xx[ok].max(), 100)
                ax.plot(grid, z[0] * grid + z[1], linewidth=1)
            ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(caption.rstrip("."))
            save_fig(fig, fname, caption)

if time_col != "—" and "Removal_%" in work.columns:
    tt = work[[time_col, "Removal_%"]].copy()
    tt[time_col] = pd.to_numeric(tt[time_col], errors="coerce")
    tt["Removal_%"] = pd.to_numeric(tt["Removal_%"], errors="coerce")
    tt = tt.dropna().sort_values(time_col)
    if not tt.empty:
        summary = tt.groupby(time_col)["Removal_%"].agg(["mean", "count", "std"]).reset_index()
        summary["err"] = summary.apply(lambda r: (1.96*r["std"]/np.sqrt(r["count"])) if r["count"] > 1 else 0, axis=1)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.errorbar(summary[time_col], summary["mean"], yerr=summary["err"], marker="o", capsize=4)
        ax.set_xlabel(str(time_col)); ax.set_ylabel("H₂S removal (%)"); ax.set_title("Figure 6. H₂S removal time course")
        save_fig(fig, "Figure_6_Removal_Time_Course", "H₂S removal efficiency over time with 95% confidence intervals.")

st.subheader("2. Publication set")
if not figures:
    st.warning("Select enough fields to generate at least one figure.")
else:
    st.success(f"Generated {len(metadata)} publication figure(s), with PNG + SVG exports at {dpi} DPI.")
    for name, caption in metadata:
        st.markdown(f"**{name.replace('_', ' ')}** — {caption}")

    package = io.BytesIO()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", "SciMantra H₂S Automatic Publication Figure Set\n\nGenerated from the active dataset. Review all figures, statistical assumptions, replicate structure, units, and journal requirements before submission.\n")
        z.writestr("figure_manifest.csv", pd.DataFrame(metadata, columns=["figure", "caption"]).to_csv(index=False))
        z.writestr("generation_metadata.txt", f"Created UTC: {datetime.now(timezone.utc).isoformat()}\nSource: {source}\nRows: {len(df)}\nDPI: {dpi}\nError bars: {error_bar}\n")
        for fname, data in figures:
            z.writestr(fname, data)
    package.seek(0)
    st.download_button("📦 Download complete Figure 1–6 ZIP", package.getvalue(), "H2S_publication_figure_set.zip", "application/zip")

    st.markdown("### ☁️ Save directly to Research Artifact Vault")
    st.caption("Save the generated publication package to a cloud research project with a SHA-256 fingerprint and provenance metadata. Your raw dataset is not modified.")
    if configured(st.secrets):
        supa = client(st.secrets)
        try:
            user = supa.auth.get_user().user
        except Exception:
            user = None
        if user:
            projects = supa.table("projects").select("id,name").order("updated_at", desc=True).execute().data or []
            if projects:
                project_map = {p["name"]: p["id"] for p in projects}
                project_name = st.selectbox("Project for Vault save", list(project_map), key="figure_vault_project")
                source_note = st.text_input("Provenance note", value="Generated by H₂S Automatic Publication Figure Set", key="figure_vault_note")
                if st.button("☁️ Save Figure Set to Project Vault", type="primary", key="save_figure_vault"):
                    try:
                        payload = package.getvalue()
                        digest = __import__('hashlib').sha256(payload).hexdigest()
                        path = upload_project_file(supa, str(user.id), project_map[project_name], "H2S_publication_figure_set.zip", payload, "application/zip")
                        create_artifact(supa, str(user.id), project_map[project_name], "H2S_publication_figure_set.zip", "package", path, "application/zip", len(payload), digest, "H₂S Automatic Publication Figure Set", {"source_dataset": source, "raw_rows": int(len(df)), "figure_count": int(len(metadata)), "note": source_note, "created_utc": datetime.now(timezone.utc).isoformat()})
                        st.success(f"Saved the complete Figure Set to **{project_name}**.")
                    except Exception as exc:
                        st.error(f"Could not save to Artifact Vault: {exc}")
            else:
                st.info("No cloud research projects found. Create one in Cloud Project Workspace first.")
        else:
            st.info("Sign in to Cloud Account to enable direct Vault saving.")
    else:
        st.caption("Direct Vault saving becomes available after Supabase Cloud is configured.")

st.info("Scientific safeguard: this engine standardizes visualization and export. It does not establish causality, statistical significance, or a globally optimal treatment. Replicate-level structure and journal-specific figure requirements must be verified before publication.")
