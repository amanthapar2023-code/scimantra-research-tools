"""SciMantra Research OS — Research Network."""
import pandas as pd
import streamlit as st
from src.scimantra.research_network import NODE_TYPES,EDGE_TYPES,new_network,add_node,add_edge,neighborhood,summary

st.set_page_config(page_title="SciMantra Research Network",page_icon="🌐",layout="wide")
st.title("🌐 SciMantra Research Network")
st.caption("Connect researchers, projects, evidence, methods and publications into a shared research network.")
st.warning("This is the network-model prototype. It does not publish private research or automatically infer scientific relationships.")
if "research_network" not in st.session_state: st.session_state.research_network=new_network()
net=st.session_state.research_network

with st.form("node"):
    c=st.columns(3); nid=c[0].text_input("Node ID"); ntype=c[1].selectbox("Node type",NODE_TYPES); label=c[2].text_input("Label")
    if st.form_submit_button("Add node",type="primary"): add_node(net,nid,ntype,label); st.success("Network node added.")

nodes={n["id"]:n for n in net["nodes"]}
if len(nodes)>=1:
    with st.form("edge"):
        c=st.columns(3); src=c[0].selectbox("Source",list(nodes)); tgt=c[1].selectbox("Target",list(nodes)); rel=c[2].selectbox("Relationship",EDGE_TYPES)
        if st.form_submit_button("Connect nodes"): add_edge(net,src,tgt,rel); st.success("Research relationship recorded.")

s=summary(net); a,b,c,d=st.columns(4); a.metric("Nodes",s["nodes"]); b.metric("Relationships",s["edges"]); c.metric("Researchers",s["researchers"]); d.metric("Projects",s["projects"])

st.subheader("Network nodes")
if net["nodes"]: st.dataframe(pd.DataFrame([{k:v for k,v in n.items() if k!="metadata"} for n in net["nodes"]]),use_container_width=True,hide_index=True)
else: st.info("Add researchers, projects and research assets to build the network.")
st.subheader("Research relationships")
if net["edges"]: st.dataframe(pd.DataFrame(net["edges"]),use_container_width=True,hide_index=True)
else: st.info("Connect nodes to record collaboration, evidence, method and publication relationships.")

if nodes:
    focus=st.selectbox("Explore a node",list(nodes))
    links=neighborhood(net,focus)
    st.write(f"**Connections for {focus}:** {len(links)}")
    if links: st.dataframe(pd.DataFrame(links),use_container_width=True,hide_index=True)
st.caption("Module 99 · Research network architecture · final integration is Module 100.")
