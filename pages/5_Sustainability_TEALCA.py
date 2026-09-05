import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from scipy.optimize import brentq

st.set_page_config(page_title="SciMantra • TEA & LCA", page_icon="🌍", layout="wide")

st.title("🌍 Sustainability & Process Evaluation")
st.caption("Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA) — transparent research decision-support tools")
st.info("Screening-level models only. Define the system boundary, functional unit, currency, year, data sources and assumptions before using results in a publication, feasibility study or investment decision.")


def irr_from_cashflows(cashflows):
    cf = np.asarray(cashflows, dtype=float)
    if len(cf) < 2 or not (np.any(cf > 0) and np.any(cf < 0)):
        return np.nan
    def npv(rate):
        return sum(v / ((1 + rate) ** i) for i, v in enumerate(cf))
    try:
        return brentq(npv, -0.9999, 100.0)
    except Exception:
        return np.nan


def payback(cashflows, discounted=False, rate=0.0):
    cumulative = 0.0
    for i, v in enumerate(cashflows):
        pv = v / ((1 + rate) ** i) if discounted else v
        previous = cumulative
        cumulative += pv
        if cumulative >= 0 and i > 0:
            if pv == 0:
                return float(i)
            return (i - 1) + max(0.0, min(1.0, -previous / pv))
    return np.nan


def tea_tool():
    st.header("💰 Techno-Economic Analysis (TEA)")
    st.write("Estimate CAPEX, annual OPEX, revenue, cash flow, NPV, IRR, payback and break-even performance for a process, product or treatment system.")

    with st.expander("1. Project & production assumptions", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            currency = st.text_input("Currency symbol", "₹")
            project_years = st.number_input("Project life (years)", 1, 50, 10)
            annual_output = st.number_input("Nameplate annual output / treatment capacity", min_value=0.000001, value=1000.0)
        with c2:
            unit = st.text_input("Output unit", "kg or m³")
            selling_price = st.number_input("Selling value / avoided treatment cost per unit", min_value=0.0, value=100.0)
            capacity_factor = st.number_input("Capacity factor (%)", 0.0, 100.0, 90.0)
        with c3:
            discount = st.number_input("Discount rate (%)", 0.0, 100.0, 10.0)
            tax = st.number_input("Tax rate (%)", 0.0, 100.0, 25.0)
            salvage_pct = st.number_input("Salvage value (% of CAPEX)", 0.0, 100.0, 5.0)

    with st.expander("2. Capital expenditure (CAPEX)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            equipment = st.number_input("Equipment & process units", min_value=0.0, value=500000.0)
            installation = st.number_input("Installation & civil works", min_value=0.0, value=150000.0)
        with c2:
            engineering = st.number_input("Engineering / commissioning", min_value=0.0, value=75000.0)
            contingency_pct = st.number_input("Contingency (%)", 0.0, 100.0, 10.0)
        with c3:
            other_capex = st.number_input("Other CAPEX", min_value=0.0, value=0.0)
            working_capital = st.number_input("Initial working capital", min_value=0.0, value=50000.0)

    direct_capex = equipment + installation + engineering + other_capex
    contingency = direct_capex * contingency_pct / 100
    total_capex = direct_capex + contingency

    with st.expander("3. Annual operating expenditure (OPEX)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            fixed_opex = st.number_input("Fixed OPEX / year", min_value=0.0, value=100000.0)
            labor = st.number_input("Labor / year", min_value=0.0, value=120000.0)
        with c2:
            utilities = st.number_input("Utilities / year", min_value=0.0, value=80000.0)
            maintenance_pct = st.number_input("Maintenance (% of CAPEX/year)", 0.0, 100.0, 4.0)
        with c3:
            variable_cost = st.number_input(f"Variable cost / {unit}", min_value=0.0, value=20.0)
            other_opex = st.number_input("Other OPEX / year", min_value=0.0, value=0.0)

    effective_output = annual_output * capacity_factor / 100
    maintenance = total_capex * maintenance_pct / 100
    revenue = effective_output * selling_price
    variable_opex = effective_output * variable_cost
    annual_opex = fixed_opex + labor + utilities + maintenance + variable_opex + other_opex
    ebitda = revenue - annual_opex
    depreciation = total_capex / project_years
    ebit = ebitda - depreciation
    tax_expense = max(0.0, ebit * tax / 100)
    nopat = ebit - tax_expense
    annual_fcf = nopat + depreciation
    salvage = total_capex * salvage_pct / 100

    cashflows = [-total_capex - working_capital] + [annual_fcf] * project_years
    cashflows[-1] += salvage + working_capital
    years = np.arange(project_years + 1)
    discounted_cf = [cashflows[i] / ((1 + discount / 100) ** i) for i in years]
    npv = sum(discounted_cf)
    irr = irr_from_cashflows(cashflows)
    simple_pb = payback(cashflows)
    discounted_pb = payback(cashflows, discounted=True, rate=discount / 100)
    break_even_price = (annual_opex + depreciation) / effective_output if effective_output else np.nan
    contribution_margin = selling_price - variable_cost
    break_even_volume = (fixed_opex + labor + utilities + maintenance + other_opex) / contribution_margin if contribution_margin > 0 else np.nan

    st.subheader("Key TEA results")
    cols = st.columns(6)
    cols[0].metric("Total CAPEX", f"{currency}{total_capex:,.0f}")
    cols[1].metric("Annual revenue", f"{currency}{revenue:,.0f}")
    cols[2].metric("Annual OPEX", f"{currency}{annual_opex:,.0f}")
    cols[3].metric("Annual FCF", f"{currency}{annual_fcf:,.0f}")
    cols[4].metric("NPV", f"{currency}{npv:,.0f}")
    cols[5].metric("IRR", f"{irr*100:.2f}%" if np.isfinite(irr) else "N/A")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Simple payback", f"{simple_pb:.2f} years" if np.isfinite(simple_pb) else "Not reached")
    c2.metric("Discounted payback", f"{discounted_pb:.2f} years" if np.isfinite(discounted_pb) else "Not reached")
    c3.metric("Break-even value / unit", f"{currency}{break_even_price:,.2f}" if np.isfinite(break_even_price) else "N/A")
    c4.metric("Break-even annual volume", f"{break_even_volume:,.2f}" if np.isfinite(break_even_volume) else "N/A")

    cf_df = pd.DataFrame({
        "Year": years,
        "Cash flow": cashflows,
        "Discounted cash flow": discounted_cf,
        "Cumulative cash flow": np.cumsum(cashflows),
        "Cumulative discounted cash flow": np.cumsum(discounted_cf),
    })
    st.subheader("Cash-flow profile")
    st.plotly_chart(px.line(cf_df, x="Year", y=["Cumulative cash flow", "Cumulative discounted cash flow"], markers=True, title="Cumulative project cash flow"), width="stretch")
    st.dataframe(cf_df, width="stretch")
    st.download_button("⬇️ Download TEA cash-flow CSV", cf_df.to_csv(index=False).encode(), "tea_cashflow.csv", "text/csv")

    st.subheader("Sensitivity analysis")
    s1, s2, s3 = st.columns(3)
    price_low = s1.number_input("Selling-value low (%)", -80.0, 0.0, -20.0)
    price_high = s2.number_input("Selling-value high (%)", 0.0, 200.0, 20.0)
    var_low = s3.number_input("Variable-cost low (%)", -80.0, 0.0, -20.0)
    var_high = st.number_input("Variable-cost high (%)", 0.0, 200.0, 20.0)
    price_grid = np.linspace(1 + price_low / 100, 1 + price_high / 100, 9)
    var_grid = np.linspace(1 + var_low / 100, 1 + var_high / 100, 9)
    rows = []
    for pm in price_grid:
        for vm in var_grid:
            r = effective_output * selling_price * pm
            vo = effective_output * variable_cost * vm
            ed = r - (fixed_opex + labor + utilities + maintenance + vo + other_opex)
            e = ed - depreciation
            tx = max(0.0, e * tax / 100)
            fcf = e - tx + depreciation
            cf = [-total_capex - working_capital] + [fcf] * project_years
            cf[-1] += salvage + working_capital
            rows.append({"Selling value multiplier": pm, "Variable-cost multiplier": vm, "NPV": sum(v / ((1 + discount / 100) ** i) for i, v in enumerate(cf))})
    sens = pd.DataFrame(rows)
    pivot = sens.pivot(index="Variable-cost multiplier", columns="Selling value multiplier", values="NPV")
    st.plotly_chart(px.imshow(pivot, aspect="auto", title="NPV sensitivity: selling value vs variable cost", labels={"x":"Selling value multiplier", "y":"Variable-cost multiplier", "color":"NPV"}), width="stretch")
    st.caption("Sensitivity holds all other assumptions constant. Use project-specific ranges and document every assumption.")


def lca_tool():
    st.header("🌍 Life Cycle Assessment (LCA)")
    st.write("Build a transparent screening LCA from material, energy, transport and emission flows, normalized to a defined functional unit.")

    with st.expander("1. Goal, scope & functional unit", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_area("Goal", "Compare the environmental burden of two process scenarios.")
            functional_unit = st.text_input("Functional unit", "1 kg product / 1 m³ treated wastewater")
            system_boundary = st.selectbox("System boundary", ["Gate-to-gate", "Cradle-to-gate", "Cradle-to-grave", "Custom"])
        with c2:
            project_name = st.text_input("Assessment name", "SciMantra screening LCA")
            reference_output = st.number_input("Reference output for inventory", min_value=0.000001, value=1000.0)
            st.caption("Enter all inventory quantities on a consistent reference basis. The tool normalizes the calculated burden to one functional unit.")

    st.subheader("2. Life-cycle inventory")
    default = pd.DataFrame([
        {"Flow":"Electricity", "Quantity":100.0, "Unit":"kWh", "Emission_factor":0.7, "EF_unit":"kg CO2e/unit", "Stage":"Operation", "Category":"Energy"},
        {"Flow":"Water", "Quantity":2.0, "Unit":"m³", "Emission_factor":0.3, "EF_unit":"kg CO2e/unit", "Stage":"Operation", "Category":"Water"},
        {"Flow":"Chemical", "Quantity":5.0, "Unit":"kg", "Emission_factor":2.0, "EF_unit":"kg CO2e/unit", "Stage":"Upstream", "Category":"Material"},
        {"Flow":"Transport", "Quantity":50.0, "Unit":"tkm", "Emission_factor":0.1, "EF_unit":"kg CO2e/unit", "Stage":"Transport", "Category":"Transport"},
    ])
    edited = st.data_editor(default, num_rows="dynamic", width="stretch", key="lca_inventory")
    inv = edited.copy()
    for col in ["Quantity", "Emission_factor"]:
        inv[col] = pd.to_numeric(inv[col], errors="coerce").fillna(0.0)
    inv["CO2e_kg"] = inv["Quantity"] * inv["Emission_factor"]
    inv["CO2e_per_FU"] = inv["CO2e_kg"] / reference_output

    st.subheader("3. Results")
    total = inv["CO2e_kg"].sum()
    per_fu = total / reference_output
    c1, c2 = st.columns(2)
    c1.metric("Total inventory GHG burden", f"{total:,.3f} kg CO₂e")
    c2.metric("GHG intensity", f"{per_fu:,.6f} kg CO₂e / functional unit")

    stage = inv.groupby("Stage", as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg", ascending=False)
    category = inv.groupby("Category", as_index=False)["CO2e_kg"].sum().sort_values("CO2e_kg", ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(stage, x="Stage", y="CO2e_kg", title="Contribution by life-cycle stage"), width="stretch")
    with c2:
        st.plotly_chart(px.bar(category, x="Category", y="CO2e_kg", title="Contribution by inventory category"), width="stretch")
    st.dataframe(inv, width="stretch")
    st.download_button("⬇️ Download LCA inventory/results CSV", inv.to_csv(index=False).encode(), "lca_inventory_results.csv", "text/csv")

    st.subheader("4. Scenario comparison")
    scenarios = st.data_editor(pd.DataFrame([
        {"Scenario":"Baseline", "Total_CO2e_kg":total},
        {"Scenario":"Alternative", "Total_CO2e_kg":total * 0.8},
    ]), num_rows="dynamic", width="stretch", key="lca_scenarios")
    scenarios = scenarios.copy()
    scenarios["Total_CO2e_kg"] = pd.to_numeric(scenarios["Total_CO2e_kg"], errors="coerce")
    scenarios["kg_CO2e_per_FU"] = scenarios["Total_CO2e_kg"] / reference_output
    baseline = scenarios.loc[scenarios["Scenario"] == "Baseline", "Total_CO2e_kg"]
    baseline_value = float(baseline.iloc[0]) if len(baseline) else float(total)
    scenarios["Reduction_vs_baseline_%"] = (baseline_value - scenarios["Total_CO2e_kg"]) / baseline_value * 100 if baseline_value else np.nan
    st.dataframe(scenarios, width="stretch")
    st.plotly_chart(px.bar(scenarios, x="Scenario", y="kg_CO2e_per_FU", title="Scenario GHG intensity"), width="stretch")
    st.download_button("⬇️ Download scenario comparison CSV", scenarios.to_csv(index=False).encode(), "lca_scenario_comparison.csv", "text/csv")

    st.subheader("5. Sensitivity analysis")
    st.caption("Screen the effect of changing one inventory flow while holding the others constant.")
    if len(inv):
        flow = st.selectbox("Flow to vary", inv["Flow"].tolist())
        row_idx = inv.index[inv["Flow"] == flow][0]
        low, high = st.slider("Quantity range (% of base)", -90, 300, (-50, 50))
        multipliers = np.linspace(1 + low / 100, 1 + high / 100, 21)
        base_total = inv["CO2e_kg"].sum()
        base_contribution = inv.loc[row_idx, "CO2e_kg"]
        values = base_total - base_contribution + base_contribution * multipliers
        sens = pd.DataFrame({"Quantity multiplier": multipliers, "Total kg CO2e": values, "kg CO2e/FU": values / reference_output})
        st.plotly_chart(px.line(sens, x="Quantity multiplier", y="kg CO2e/FU", markers=True, title=f"LCA sensitivity: {flow}"), width="stretch")
        st.download_button("⬇️ Download LCA sensitivity CSV", sens.to_csv(index=False).encode(), "lca_sensitivity.csv", "text/csv")

    with st.expander("Important LCA interpretation notes"):
        st.markdown("- Emission factors are user-supplied and should be traceable to a recognized database, EPD, literature source, supplier data or measured inventory.\n- This screening tool currently reports a user-defined GHG/CO₂e indicator; it is not a full ISO-conformant multi-impact LCA database.\n- Do not mix mass, energy, distance or transport units without appropriate emission factors.\n- Document allocation rules, cut-offs, co-products, geographic scope, electricity mix, uncertainty and data year in research reporting.")


choice = st.sidebar.radio("Choose analysis", ["💰 Techno-Economic Analysis", "🌍 Life Cycle Assessment"])
if choice.startswith("💰"):
    tea_tool()
else:
    lca_tool()

st.divider()
st.caption("SciMantra Research Tools • Educational/research decision-support. Verify assumptions, methods, emission factors, financial conventions and applicable standards before publication or investment decisions.")
