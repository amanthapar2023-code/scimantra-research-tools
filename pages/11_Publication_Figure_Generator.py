import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SciMantra Publication Figure Generator", page_icon="📈", layout="wide")
st.title("📈 SciMantra Publication Figure Generator")
st.caption("Create research-ready exploratory figures from CSV/Excel data. Always verify labels, statistics and experimental design before publication.")

if "figure_df" not in st.session_state:
    st.session_state.figure_df = None

uploaded = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
if uploaded:
    try:
        st.session_state.figure_df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Could not read dataset: {exc}")

df = st.session_state.figure_df
if df is None:
    st.info("Upload a dataset to start generating figures.")
    st.stop()

numeric = list(df.select_dtypes(include="number").columns)
all_cols = list(df.columns)
if not numeric:
    st.warning("No numeric variables were detected.")
    st.stop()

st.success(f"Loaded {len(df):,} rows × {len(df.columns):,} columns")

figure_type = st.selectbox("Figure type", [
    "Group mean ± SD",
    "Group mean ± SEM",
    "Individual replicates",
    "Scatter + regression",
    "Correlation heatmap",
    "Time-course",
    "Histogram",
])

st.subheader("Figure settings")
title = st.text_input("Figure title", "Research data")
x_label = st.text_input("X-axis label", "")
y_label = st.text_input("Y-axis label", "")
fig_width = st.slider("Width", 5, 14, 8)
fig_height = st.slider("Height", 4, 10, 6)
font_size = st.slider("Font size", 8, 22, 12)

fig = None

if figure_type in ["Group mean ± SD", "Group mean ± SEM", "Individual replicates"]:
    y = st.selectbox("Response variable", numeric)
    group_candidates = [c for c in all_cols if c != y]
    group = st.selectbox("Group / treatment column", group_candidates if group_candidates else [y])
    work = pd.DataFrame({"group": df[group].astype(str), "value": pd.to_numeric(df[y], errors="coerce")}).dropna()
    grouped = work.groupby("group")["value"]
    stats_df = grouped.agg(["count", "mean", "std"]).reset_index()
    stats_df["sem"] = stats_df["std"] / np.sqrt(stats_df["count"].clip(lower=1))

    st.dataframe(stats_df.round(5), width="stretch", hide_index=True)
    if st.button("Generate figure", type="primary"):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        x = np.arange(len(stats_df))
        if figure_type == "Individual replicates":
            for i, (name, vals) in enumerate(grouped):
                jitter = np.linspace(-0.12, 0.12, len(vals)) if len(vals) > 1 else np.array([0.0])
                ax.scatter(np.full(len(vals), i) + jitter, vals, alpha=0.8, s=35)
            ax.set_xticks(x, stats_df["group"])
        else:
            err = stats_df["sd"] if "SD" in figure_type else stats_df["sem"]
            ax.errorbar(x, stats_df["mean"], yerr=err, fmt="o", capsize=5, markersize=7, linewidth=1.5)
            ax.set_xticks(x, stats_df["group"])
        ax.set_title(title, fontsize=font_size + 2)
        ax.set_xlabel(x_label or str(group), fontsize=font_size)
        ax.set_ylabel(y_label or str(y), fontsize=font_size)
        ax.tick_params(axis="both", labelsize=font_size - 1)
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()

elif figure_type == "Scatter + regression":
    x = st.selectbox("X variable", numeric)
    y = st.selectbox("Y variable", [c for c in numeric if c != x] or numeric)
    work = pd.DataFrame({"x": pd.to_numeric(df[x], errors="coerce"), "y": pd.to_numeric(df[y], errors="coerce")}).dropna()
    if st.button("Generate figure", type="primary"):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.scatter(work["x"], work["y"], alpha=0.8, s=38)
        if len(work) >= 3 and work["x"].nunique() > 1:
            slope, intercept = np.polyfit(work["x"], work["y"], 1)
            xx = np.linspace(work["x"].min(), work["x"].max(), 100)
            ax.plot(xx, slope * xx + intercept, linewidth=2)
            r = np.corrcoef(work["x"], work["y"])[0, 1]
            ax.text(0.03, 0.97, f"r = {r:.3f}\nR² = {r**2:.3f}", transform=ax.transAxes, va="top", fontsize=font_size)
        ax.set_title(title, fontsize=font_size + 2)
        ax.set_xlabel(x_label or str(x), fontsize=font_size)
        ax.set_ylabel(y_label or str(y), fontsize=font_size)
        ax.tick_params(axis="both", labelsize=font_size - 1)
        ax.grid(alpha=0.2)
        fig.tight_layout()

elif figure_type == "Correlation heatmap":
    corr = df[numeric].corr()
    if st.button("Generate figure", type="primary"):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        image = ax.imshow(corr, vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(corr.columns)), corr.columns)
        for i in range(len(corr)):
            for j in range(len(corr)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=max(font_size - 3, 7))
        fig.colorbar(image, ax=ax, label="Correlation")
        ax.set_title(title, fontsize=font_size + 2)
        fig.tight_layout()

elif figure_type == "Time-course":
    x = st.selectbox("Time variable", all_cols)
    y = st.selectbox("Response variable", numeric)
    group_options = ["None"] + [c for c in all_cols if c not in [x, y]]
    group = st.selectbox("Optional group", group_options)
    if st.button("Generate figure", type="primary"):
        work = pd.DataFrame({"x": df[x], "y": pd.to_numeric(df[y], errors="coerce")}).dropna()
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        if group != "None":
            work["group"] = df.loc[work.index, group].astype(str)
            for name, sub in work.groupby("group"):
                sub = sub.sort_values("x")
                ax.plot(sub["x"], sub["y"], marker="o", label=name)
            ax.legend(title=group)
        else:
            work = work.sort_values("x")
            ax.plot(work["x"], work["y"], marker="o")
        ax.set_title(title, fontsize=font_size + 2)
        ax.set_xlabel(x_label or str(x), fontsize=font_size)
        ax.set_ylabel(y_label or str(y), fontsize=font_size)
        ax.tick_params(axis="both", labelsize=font_size - 1)
        ax.grid(alpha=0.2)
        fig.tight_layout()

else:
    x = st.selectbox("Variable", numeric)
    bins = st.slider("Bins", 5, 60, 20)
    if st.button("Generate figure", type="primary"):
        values = pd.to_numeric(df[x], errors="coerce").dropna()
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.hist(values, bins=bins, alpha=0.8)
        ax.set_title(title, fontsize=font_size + 2)
        ax.set_xlabel(x_label or str(x), fontsize=font_size)
        ax.set_ylabel(y_label or "Frequency", fontsize=font_size)
        ax.tick_params(axis="both", labelsize=font_size - 1)
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()

if fig is not None:
    st.subheader("Publication figure preview")
    st.pyplot(fig)
    png = io.BytesIO()
    svg = io.StringIO()
    fig.savefig(png, format="png", dpi=600, bbox_inches="tight")
    fig.savefig(svg, format="svg", bbox_inches="tight")
    st.download_button("⬇️ Download 600-DPI PNG", png.getvalue(), "scimantra_publication_figure.png", "image/png")
    st.download_button("⬇️ Download SVG", svg.getvalue(), "scimantra_publication_figure.svg", "image/svg+xml")
    plt.close(fig)

st.info("Tip: use individual-replicate plots when possible. Error bars should be labeled explicitly (SD, SEM, or confidence interval) and match the statistical analysis reported in your manuscript.")
