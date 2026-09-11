"""Append-only research workflow audit trail primitives."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

ACTIONS=["Created","Updated","Status changed","Linked","Unlinked","Approved","Archived","Exported"]

def event(actor:str,action:str,entity_type:str,entity_id:str,details:str="")->dict[str,Any]:
    return {"timestamp":datetime.now(timezone.utc).isoformat(),"actor":actor,"action":action,"entity_type":entity_type,"entity_id":entity_id,"details":details}

def append(log:list[dict[str,Any]],record:dict[str,Any])->list[dict[str,Any]]:
    log.append(dict(record)); return log

def audit(log:list[dict[str,Any]])->dict[str,int]:
    return {"events":len(log),"actors":len({x.get("actor","") for x in log if x.get("actor")}),"entities":len({(x.get("entity_type"),x.get("entity_id")) for x in log})}

def history(log:list[dict[str,Any]],entity_id:str)->list[dict[str,Any]]:
    return [x for x in log if x.get("entity_id")==entity_id]
