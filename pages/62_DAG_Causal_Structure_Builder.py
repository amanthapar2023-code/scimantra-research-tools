import pandas as pd
import streamlit as st

from scimantra.dag_builder import (
    EDGE_TYPES,
    NODE_ROLES,
    adjustment_guidance,
    audit_dag,
    build_starter_dag,
    edge,
    export_dag,
    node,
)

st.set_page_config(page_title="DAG & Causal Structure Builder | SciMantra", layout="wide")
st.title("DAG & Causal Structure Builder")
st.caption("Map your proposed causal structure before deciding what to adjust for.")
st.warning("Integrity rule: arrows and variable roles are researcher-review hypotheses. This tool does not discover the true causal graph or prove causality.")

col1, col2 = st.columns(2)
with col1:
    exposure = st.text_input("Primary exposure / intervention")
    outcome = st.text_input("Primary outcome")
    conf_text = st.text_area("Candidate confounders (one per line)", placeholder="Age\nBatch\nBaseline measurement")
with col2:
    st.markdown("**Variable roles**")
    st.caption("Confounder = candidate common cause; mediator = possible pathway; collider = possible common effect. Labels require domain justification.")

if st.button("Build starter DAG", type="primary", use_container_width=True):
    conf = [x.strip() for x in conf_text.splitlines() if x.strip()]
    n, e = build_starter_dag(exposure, outcome, conf)
    st.session_state["dag_nodes"] = n
    st.session_state["dag_edges"] = e

nodes = st.session_state.get("dag_nodes", [])
edges = st.session_state.get("dag_edges", [])

if nodes:
    st.subheader("1. Variable map")
    for i, item in enumerate(nodes):
        c1, c2 = st.columns([2, 1])
        with c1:
            item["Variable"] = st.text_input("Variable", item["Variable"], key=f"dag_var_{i}")
            item["Rationale"] = st.text_input("Why this role?", item.get("Rationale", ""), key=f"dag_rat_{i}")
        with c2:
            item["Role"] = st.selectbox("Role", NODE_ROLES, index=NODE_ROLES.index(item.get("Role", "Unclassified")), key=f"dag_role_{i}")

    st.subheader("2. Relationships")
    for i, item in enumerate(edges):
        c1, c2, c3 = st.columns([2, 2, 1])
        names = [n["Variable"] for n in nodes if n.get("Variable", "").strip()]
        with c1:
            item["From"] = st.selectbox("From", names, index=names.index(item["From"]) if item["From"] in names else 0, key=f"dag_from_{i}")
        with c2:
            item["To"] = st.selectbox("To", names, index=names.index(item["To"]) if item["To"] in names else 0, key=f"dag_to_{i}")
        with c3:
            item["Relationship"] = st.selectbox("Type", EDGE_TYPES, index=EDGE_TYPES.index(item.get("Relationship", EDGE_TYPES[0])), key=f"dag_rel_{i}")
        item["Rationale"] = st.text_input("Relationship rationale", item.get("Rationale", ""), key=f"dag_edge_rat_{i}")

    with st.expander("Add a relationship"):
        names = [n["Variable"] for n in nodes if n.get("Variable", "").strip()]
        if len(names) >= 2:
            f = st.selectbox("From variable", names, key="dag_new_from")
            t = st.selectbox("To variable", names, key="dag_new_to")
            r = st.selectbox("Relationship", EDGE_TYPES, key="dag_new_rel")
            rr = st.text_input("Why do you propose this relationship?", key="dag_new_reason")
            if st.button("Add relationship"):
                edges.append(edge(f, t, r, rr))
                st.rerun()

    audit = audit_dag(nodes, edges)
    st.subheader("3. Structural audit")
    a, b, c, d = st.columns(4)
    a.metric("Variables", audit["nodes"])
    b.metric("Relationships", audit["edges"])
    c.metric("Isolated", len(audit["isolated_nodes"]))
    d.metric("Status", audit["structural_status"])

    if audit["duplicate_nodes"]:
        st.error("Duplicate variable names: " + ", ".join(audit["duplicate_nodes"]))
    if audit["dangling_edges"]:
        st.error(f"{audit['dangling_edges']} relationship(s) reference missing variables.")
    if audit["mediator_adjustment_warning"]:
        st.warning("Mediator review: " + ", ".join(audit["mediator_adjustment_warning"]) + ". Do not automatically adjust for a mediator; define the estimand first.")
    if audit["collider_warning"]:
        st.warning("Collider review: " + ", ".join(audit["collider_warning"]) + ". Conditioning may create a non-causal association; justify any adjustment.")

    st.subheader("4. Adjustment decision aid")
    st.dataframe(pd.DataFrame(adjustment_guidance(nodes)), use_container_width=True, hide_index=True)
    st.caption("This is guidance for discussion, not an automatic adjustment-set calculator.")

    st.subheader("5. DAG documentation")
    st.code("\n".join(f"{e['From']} → {e['To']} [{e['Relationship']}]" for e in edges) or "No relationships defined.")
    st.download_button("Download DAG plan (Markdown)", export_dag(nodes, edges, audit), "scimantra_dag_plan.md", "text/markdown", use_container_width=True)
else:
    st.info("Enter an exposure, outcome, and optional candidate confounders to construct a starter causal structure.")
