import streamlit as st
import pandas as pd
from src.scimantra.synthetic_pilot import simulate_two_group, simulation_sensitivity, summarize_sensitivity, export_pilot

st.set_page_config(page_title="Synthetic Pilot Lab | SciMantra", page_icon="🧪", layout="wide")
st.title("🧪 Synthetic Pilot Lab")
st.caption("Stress-test an experimental idea with simulated observations before committing real samples, time, or resources.")

st.warning("SIMULATION ONLY — every observation generated here is synthetic. Nothing from this page is experimental evidence and must not be reported as real data.")

c1, c2 = st.columns(2)
with c1:
    n_control = st.number_input("Synthetic control replicates", 2, 1000, 10)
    control_mean = st.number_input("Assumed control mean", value=100.0)
    n_treatment = st.number_input("Synthetic treatment replicates", 2, 1000, 10)
with c2:
    treatment_mean = st.number_input("Assumed treatment mean", value=110.0)
    sd = st.number_input("Assumed within-group SD", min_value=0.0001, value=10.0)
    seed = st.number_input("Random seed", 0, 1000000, 42)

repeats = st.slider("Sensitivity simulations", 10, 500, 100)

if st.button("▶️ Run synthetic pilot", type="primary"):
    params = {"Control n": n_control, "Treatment n": n_treatment, "Control mean": control_mean, "Treatment mean": treatment_mean, "Assumed SD": sd, "Seed": seed, "Sensitivity repeats": repeats}
    df, one = simulate_two_group(n_control, n_treatment, control_mean, treatment_mean, sd, seed)
    sens = simulation_sensitivity(n_control, n_treatment, control_mean, treatment_mean, sd, repeats, seed)
    st.session_state.synthetic_pilot = (params, df, one, sens)

if "synthetic_pilot" in st.session_state:
    params, df, one, sens = st.session_state.synthetic_pilot
    st.divider()
    a, b, c = st.columns(3)
    a.metric("Synthetic difference", f"{one['Observed synthetic difference']:.3g}")
    b.metric("Synthetic standardized difference", f"{one['Standardized difference']:.3g}")
    ss = summarize_sensitivity(sens)
    c.metric("Simulated difference range", f"{ss['5th percentile']:.3g} to {ss['95th percentile']:.3g}")

    st.subheader("1. One synthetic dataset")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("2. Sampling-variability stress test")
    st.dataframe(sens, use_container_width=True, hide_index=True)
    st.write(ss)

    st.subheader("3. What this can reveal")
    for item in [
        "Whether the assumed effect is large relative to assumed variability.",
        "How much the estimated difference changes across repeated synthetic samples.",
        "Whether the proposed replication level appears unstable under the assumptions you supplied.",
        "Which assumptions should be replaced with pilot or literature-supported estimates before final planning.",
    ]:
        st.write("• " + item)

    st.download_button("⬇️ Export synthetic pilot report", export_pilot(params, one, ss), "synthetic_pilot_report.md", "text/markdown")

st.info("Integrity rule: the simulation does not estimate real-world treatment effects, statistical significance, power, or publication probability. Replace assumptions with defensible inputs and use the appropriate field-specific design and power-analysis methods before collecting real data.")
