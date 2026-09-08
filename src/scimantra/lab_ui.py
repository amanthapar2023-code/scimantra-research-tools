from __future__ import annotations

import streamlit as st

from src.scimantra.laboratory import (
    biomass_concentration,
    bod_approx,
    cfu_per_ml,
    cod_from_titration,
    dilution_stock_volume,
    growth_rate,
    molarity_from_mass,
    normality_from_molarity,
    solution_percentage,
    specific_growth_rate,
)


def render() -> None:
    st.markdown("## 🧪 Laboratory Calculators")
    st.caption("Fast, transparent calculations for routine laboratory and biotechnology work.")

    st.markdown(
        '<div class="hero"><div class="eyebrow">Laboratory toolkit</div>'
        '<h1 style="font-size:2rem;margin:0">Calculate with confidence</h1>'
        '<p>Enter your experimental values, review the equation inputs, and export the result for your research record.</p></div>',
        unsafe_allow_html=True,
    )

    categories = {
        "🧴 Solutions": ["Molarity", "Dilution", "% Solution", "Normality"],
        "🧫 Microbiology": ["CFU/mL", "Biomass concentration"],
        "📈 Growth": ["Growth rate", "Specific growth rate"],
        "🌊 Water & wastewater": ["BOD₅", "COD"],
    }
    category = st.selectbox("Calculator category", list(categories))
    tool = st.selectbox("Choose calculation", categories[category])

    st.divider()
    left, right = st.columns([1.25, 1], gap="large")

    with left:
        st.markdown("### Input values")
        if tool == "Molarity":
            mass = st.number_input("Mass of solute (g)", min_value=0.0, value=1.0)
            mw = st.number_input("Molecular weight (g/mol)", min_value=1e-12, value=58.44)
            vol = st.number_input("Final volume (L)", min_value=1e-12, value=1.0)
            result = molarity_from_mass(mass, mw, vol)
            unit = "mol/L"
            equation = "M = mass ÷ (molecular weight × volume)"
        elif tool == "Dilution":
            c1 = st.number_input("Stock concentration C₁", min_value=0.0, value=100.0)
            c2 = st.number_input("Target concentration C₂", min_value=1e-12, value=10.0)
            v2 = st.number_input("Final volume V₂", min_value=1e-12, value=100.0)
            try:
                v1 = dilution_stock_volume(c1, c2, v2)
                result = v1
                unit = "same volume unit as V₂"
                equation = "C₁V₁ = C₂V₂"
            except ValueError as exc:
                st.error(str(exc)); return
        elif tool == "% Solution":
            st.selectbox("Solution basis", ["w/v", "w/w", "v/v"])
            amount = st.number_input("Solute amount", min_value=0.0, value=5.0)
            total = st.number_input("Final amount/volume", min_value=1e-12, value=100.0)
            result = solution_percentage(amount, total); unit = "%"; equation = "% = solute ÷ final amount × 100"
        elif tool == "Normality":
            m = st.number_input("Molarity (mol/L)", min_value=0.0, value=1.0)
            n = st.number_input("n-factor", min_value=1e-12, value=1.0)
            result = normality_from_molarity(m, n); unit = "N"; equation = "N = M × n-factor"
        elif tool == "CFU/mL":
            colonies = st.number_input("Colonies counted", min_value=0.0, value=125.0)
            dilution = st.number_input("Reciprocal dilution factor", min_value=1.0, value=100000.0)
            plated = st.number_input("Volume plated (mL)", min_value=1e-12, value=0.1)
            result = cfu_per_ml(colonies, dilution, plated); unit = "CFU/mL"; equation = "CFU/mL = colonies × dilution factor ÷ plated volume"
        elif tool == "Biomass concentration":
            dry = st.number_input("Dry biomass (g)", min_value=0.0, value=1.0)
            vol = st.number_input("Culture volume (L)", min_value=1e-12, value=1.0)
            result = biomass_concentration(dry, vol); unit = "g/L"; equation = "Biomass concentration = dry biomass ÷ culture volume"
        elif tool == "Growth rate":
            x1 = st.number_input("Measurement X₁", value=0.1)
            x2 = st.number_input("Measurement X₂", value=0.8)
            t1 = st.number_input("Time t₁", value=0.0)
            t2 = st.number_input("Time t₂", value=10.0)
            try: result = growth_rate(x1, x2, t1, t2)
            except ValueError as exc: st.error(str(exc)); return
            unit = "measurement/time"; equation = "Growth rate = (X₂ − X₁) ÷ (t₂ − t₁)"
        elif tool == "Specific growth rate":
            x1 = st.number_input("X₁", min_value=1e-12, value=0.1)
            x2 = st.number_input("X₂", min_value=1e-12, value=0.8)
            dt = st.number_input("Δt", min_value=1e-12, value=10.0)
            result = specific_growth_rate(x1, x2, dt); unit = "time⁻¹"; equation = "μ = ln(X₂/X₁) ÷ Δt"
        elif tool == "BOD₅":
            initial = st.number_input("Initial DO (mg/L)", value=8.0)
            final = st.number_input("Final DO (mg/L)", value=3.0)
            sample = st.number_input("Sample volume (mL)", min_value=1e-12, value=15.0)
            bottle = st.number_input("Bottle volume (mL)", min_value=1e-12, value=300.0)
            result = bod_approx(initial, final, sample, bottle); unit = "mg/L"; equation = "Approx. BOD₅ from dissolved oxygen depletion and dilution"
        else:
            blank = st.number_input("Blank titration A (mL)", value=20.0)
            sample = st.number_input("Sample titration B (mL)", value=12.0)
            normality = st.number_input("Titrant normality", min_value=1e-12, value=0.1)
            volume = st.number_input("Sample volume (mL)", min_value=1e-12, value=10.0)
            result = cod_from_titration(blank, sample, normality, volume); unit = "mg/L"; equation = "COD from titration difference, titrant normality and sample volume"

    with right:
        st.markdown("### Result")
        st.metric("Calculated value", f"{result:.6g}", unit)
        st.success("Calculation completed")
        st.markdown("**Equation / method**")
        st.code(equation)
        st.caption("Use consistent units throughout the calculation. Results should be checked against your laboratory SOP, method standard and experimental context.")

    st.divider()
    st.markdown("### 📝 Research record")
    st.info("Record the input values, units, method/reference and final result in your laboratory notebook or project record. SciMantra provides calculation support; it does not replace validated laboratory methods.")
