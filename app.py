import math
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
from scipy.optimize import brentq
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SciMantra Research Tools", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container { max-width: 1400px; padding-top: 1.5rem; }
.hero { padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(135deg,#e8f3ff,#f8fbff); border: 1px solid #d7e8fa; margin-bottom: 1rem; }
.hero h1 { margin:0; color:#0b1f33; font-size:2.35rem; }
.hero p { margin:.4rem 0 0; color:#38536b; font-size:1.05rem; }
.tool-card { border:1px solid #e3eaf0; border-radius:14px; padding:1rem; background:white; min-height:120px; }
.formula { background:#f7f9fb; padding:.7rem 1rem; border-radius:10px; border-left:4px solid #1565c0; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🔬 SciMantra Research Tools</h1>
<p>Calculate • Analyze • Visualize • Understand — practical tools for science, laboratory work and research.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("SCIMantra")
st.sidebar.caption("Science • Research • Learning")
section = st.sidebar.radio("Choose a tool", [
    "🏠 Dashboard", "🧪 Laboratory Calculators", "📊 Statistics",
    "🌱 Environmental Biotechnology", "📈 Data Analyzer", "📊 Advanced Experimental Data Analysis", "🔬 Research Tools", "🌍 TEA & LCA"
])

def download_df(df, filename="scimantra_results.csv"):
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), filename, "text/csv")

if section == "📊 Advanced Experimental Data Analysis":
    import runpy
    runpy.run_path("pages/7_Advanced_Experimental_Data_Analysis.py")
    st.stop()

# The remainder of the existing application follows unchanged.
