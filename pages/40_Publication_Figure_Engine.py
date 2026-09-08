import streamlit as st
import pandas as pd
from src.scimantra.publication_figures import figure_types, make_figure, figure_png

st.set_page_config(page_title="Publication Figure Engine | SciMantra", page_icon="📈", layout="wide")
st.title("📈 Publication Figure Engine")
st.caption("Generate reproducible, high-resolution exploratory figures directly from your actual dataset.")

uploaded = st.file_uploader("Upload CSV data", type=["csv"])
if uploaded is None:
    st.info("Upload the dataset used for your analysis. Figures are generated only from supplied observations.")
    st.stop()

df = pd.read_csv(uploaded)
numeric = list(df.select_dtypes(include="number").columns)
all_cols = list(df.columns)
if not numeric or len(all_cols) < 2:
    st.error("The dataset needs at least one numeric variable and a second column.")
    st.stop()

x = st.selectbox("X / grouping variable", all_cols)
y = st.selectbox("Y / numeric outcome", numeric)
kind = st.selectbox("Figure type", figure_types())

st.caption("Choose the figure type according to the data structure and research question. The tool does not decide scientific significance from the plot.")
if st.button("Generate figure", type="primary", use_container_width=True):
    fig = make_figure(df, kind, x, y)
    st.pyplot(fig, use_container_width=True)
    png = figure_png(fig) if False else None
    # Regenerate for download because the display call may close the figure.
    fig2 = make_figure(df, kind, x, y)
    png = figure_png(fig2)
    st.download_button("⬇️ Download 300-dpi PNG", png, "scimantra_publication_figure.png", "image/png", use_container_width=True)

st.divider()
st.subheader("Figure integrity checklist")
for item in [
    "Confirm the plotted unit is the true experimental/observational unit.",
    "Show individual observations when appropriate; do not hide replication behind summary bars.",
    "Verify axis units, transformations, labels, and time ordering before submission.",
    "Keep the original dataset and analysis settings so the figure is reproducible.",
    "Do not use a visual pattern alone as evidence of causality or statistical significance.",
]:
    st.write("☐ " + item)
