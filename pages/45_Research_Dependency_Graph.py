import streamlit as st
import pandas as pd
from src.scimantra.research_graph import NODE_TYPES, EDGE_TYPES, node, edge, graph_audit, export_graph

st.set_page_config(page_title="Research Dependency Graph | SciMantra", page_icon="🕸️", layout="wide")
st.title("🕸️ Research Dependency Graph")
st.caption("Connect the objects of a study so unsupported jumps in reasoning become visible.")

if "graph_nodes" not in st.session_state: st.session_state.graph_nodes = []
if "graph_edges" not in st.session_state: st.session_state.graph_edges = []

with st.expander("Add research node", expanded=True):
    c1, c2, c3 = st.columns(3)
    nid = c1.text_input("Node ID", placeholder="H1")
    ntype = c2.selectbox("Type", NODE_TYPES)
    label = c3.text_input("Description", placeholder="Primary hypothesis")
    source = st.text_input("Source / provenance (optional)")
    if st.button("Add node") and nid.strip() and label.strip():
        if not any(n["id"] == nid.strip() for n in st.session_state.graph_nodes):
            st.session_state.graph_nodes.append(node(nid, ntype, label, source))

if st.session_state.graph_nodes:
    with st.expander("Connect nodes", expanded=True):
        ids = [n["id"] for n in st.session_state.graph_nodes]
        c1, c2, c3 = st.columns(3)
        src = c1.selectbox("From", ids)
        rel = c2.selectbox("Relationship", EDGE_TYPES)
        dst = c3.selectbox("To", ids)
        if st.button("Add relationship") and src != dst:
            st.session_state.graph_edges.append(edge(src, rel, dst))

if st.session_state.graph_nodes:
    audit = graph_audit(st.session_state.graph_nodes, st.session_state.graph_edges)
    a, b, c, d = st.columns(4)
    a.metric("Nodes", audit["nodes"]); b.metric("Relationships", audit["edges"])
    c.metric("Isolated nodes", audit["isolated_nodes"]); d.metric("Connected", f"{audit['connected_percent']}%")
    st.subheader("Nodes")
    st.dataframe(pd.DataFrame(st.session_state.graph_nodes), use_container_width=True, hide_index=True)
    st.subheader("Relationships")
    st.dataframe(pd.DataFrame(st.session_state.graph_edges), use_container_width=True, hide_index=True)
    st.download_button("Export graph as Markdown", export_graph(st.session_state.graph_nodes, st.session_state.graph_edges), "research_dependency_graph.md", "text/markdown")
else:
    st.info("Start by adding your research question, hypothesis, experiment, dataset, analysis, result, claim, evidence, and conclusion as nodes.")

st.warning("A connected graph does not prove scientific validity. It makes the reasoning chain explicit so the researcher can inspect missing links.")
