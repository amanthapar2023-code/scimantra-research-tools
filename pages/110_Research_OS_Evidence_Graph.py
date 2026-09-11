"""Phase 110 — Research OS Evidence Graph."""
import pandas as pd
import streamlit as st
from scimantra.research_os_data_bus import new_bus
from scimantra.research_os_evidence_graph import audit_graph, build_graph, claim_coverage, summary, trace

st.set_page_config(page_title="SciMantra — Evidence Graph", page_icon="🕸️", layout="wide")
st.title("🕸️ Phase 110 — Research OS Evidence Graph")
st.caption("Trace the explicit chain from literature/evidence to analysis, results, claims and manuscript outputs.")
st.info("This graph shows researcher-recorded relationships. A linked claim is not automatically scientifically supported or true.")
if "research_os_bus" not in st.session_state: st.session_state.research_os_bus=new_bus()
graph=build_graph(st.session_state.research_os_bus); a=audit_graph(graph); s=summary(graph)
c=st.columns(4); c[0].metric("Nodes",s["nodes"]); c[1].metric("Edges",s["edges"]); c[2].metric("Claims",s["claims"]); c[3].metric("Claims without links",s["claims_without_incoming"])

t1,t2,t3=st.tabs(["Graph inventory","Claim coverage","Trace evidence"])
with t1:
    st.subheader("Evidence graph inventory")
    if graph["nodes"]: st.dataframe(pd.DataFrame(graph["nodes"]),use_container_width=True,hide_index=True)
    else: st.info("Register artifacts and links in the shared Research OS bus first.")
    if graph["edges"]: st.dataframe(pd.DataFrame(graph["edges"]),use_container_width=True,hide_index=True)
with t2:
    rows=claim_coverage(graph)
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("No Claim artifacts are currently registered.")
    if a["unsupported_claims"]: st.warning("Claims without incoming evidence/relationship links: "+", ".join(a["unsupported_claims"]))
with t3:
    ids=[n["id"] for n in graph["nodes"] if n.get("id")]
    if ids:
        node=st.selectbox("Artifact to trace",ids); direction=st.radio("Direction",["upstream","downstream"],horizontal=True)
        rows=trace(graph,node,direction)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.info("No linked nodes found in that direction.")
    else: st.info("No graph nodes available.")

st.divider()
if a["broken_edges"]: st.error("Broken graph links detected.")
elif a["healthy"]: st.success("Graph structure passes the basic integrity check.")
st.caption("Phase 110 boundary: provenance and relationship visibility only; linkage does not establish scientific validity.")
