"""Collaborative research project coordination primitives."""
from __future__ import annotations
from typing import Any

ROLES=["PI / Lead","Researcher","Student","Analyst","Collaborator","Reviewer"]
TASK_STATUSES=["Backlog","In progress","Blocked","Review","Complete"]

def project_summary(members:list[dict[str,Any]],tasks:list[dict[str,Any]])->dict[str,int]:
    return {"members":len(members),"tasks":len(tasks),"active":sum(t.get("status")=="In progress" for t in tasks),"blocked":sum(t.get("status")=="Blocked" for t in tasks),"complete":sum(t.get("status")=="Complete" for t in tasks)}

def priority_tasks(tasks:list[dict[str,Any]])->list[dict[str,Any]]:
    rank={"High":0,"Medium":1,"Low":2}
    return sorted([t for t in tasks if t.get("status")!="Complete"],key=lambda x:rank.get(x.get("priority"),9))
