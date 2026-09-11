"""Reviewer response and revision tracking for SciMantra Research OS."""
from __future__ import annotations
from typing import Any

SEVERITIES=["Major","Minor","Editorial","Required experiment"]
STATUSES=["Open","In progress","Resolved","Not applicable"]

def audit(items:list[dict[str,Any]])->dict[str,Any]:
    open_items=[x for x in items if x.get("status","Open") in ("Open","In progress")]
    major=[x for x in open_items if x.get("severity") in ("Major","Required experiment")]
    return {"total":len(items),"open":len(open_items),"major_open":len(major),"resolved":sum(x.get("status")=="Resolved" for x in items),"ready":bool(items) and not major}

def priority_queue(items:list[dict[str,Any]])->list[dict[str,Any]]:
    rank={"Required experiment":0,"Major":1,"Minor":2,"Editorial":3}
    return sorted([x for x in items if x.get("status")!="Resolved"],key=lambda x:rank.get(x.get("severity"),9))

def response_template(comment:str="")->dict[str,Any]:
    return {"id":"","reviewer":"","round":"1","severity":"Major","comment":comment,"location":"","response":"","revision":"","evidence":"","status":"Open"}
