"""Research Network primitives for SciMantra."""
from __future__ import annotations
from typing import Any

NODE_TYPES=["Researcher","Project","Method","Evidence","Dataset","Publication","Research question","Research gap","Hypothesis"]
EDGE_TYPES=["owns","contributes_to","uses","supports","produces","cites","addresses","tests","collaborates_on"]

def new_network()->dict[str,Any]: return {"nodes":[],"edges":[]}

def add_node(net:dict[str,Any],node_id:str,node_type:str,label:str,metadata:dict[str,Any]|None=None):
    if node_type not in NODE_TYPES: raise ValueError("Unsupported node type")
    n={"id":node_id,"type":node_type,"label":label,"metadata":metadata or {}}; net["nodes"].append(n); return n

def add_edge(net:dict[str,Any],source:str,target:str,relation:str):
    if relation not in EDGE_TYPES: raise ValueError("Unsupported relation")
    e={"source":source,"target":target,"relation":relation}; net["edges"].append(e); return e

def neighborhood(net:dict[str,Any],node_id:str):
    return [e for e in net.get("edges",[]) if e.get("source")==node_id or e.get("target")==node_id]

def summary(net:dict[str,Any]):
    return {"nodes":len(net.get("nodes",[])),"edges":len(net.get("edges",[])),"researchers":sum(n.get("type")=="Researcher" for n in net.get("nodes",[])),"projects":sum(n.get("type")=="Project" for n in net.get("nodes",[]))}
