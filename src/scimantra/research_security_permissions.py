"""Project-level role and permission model for SciMantra."""
from __future__ import annotations
from typing import Any

ROLES={"PI / Admin":{"view":True,"edit":True,"approve":True,"export":True,"manage":True},"Researcher":{"view":True,"edit":True,"approve":False,"export":True,"manage":False},"Student":{"view":True,"edit":True,"approve":False,"export":False,"manage":False},"Analyst":{"view":True,"edit":True,"approve":False,"export":True,"manage":False},"Collaborator":{"view":True,"edit":False,"approve":False,"export":False,"manage":False},"Reviewer":{"view":True,"edit":False,"approve":True,"export":False,"manage":False}}

def can(role:str,action:str)->bool:return bool(ROLES.get(role,{}).get(action,False))
def audit_members(members:list[dict[str,Any]])->dict[str,Any]:
    unknown=[m.get("name","") for m in members if m.get("role") not in ROLES]
    return {"members":len(members),"unknown_roles":unknown,"admins":sum(m.get("role")=="PI / Admin" for m in members)}
