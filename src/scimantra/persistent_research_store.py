"""Database-ready persistent research store schema for SciMantra."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

ENTITY_TYPES=["project","member","artifact","evidence","experiment","dataset","analysis","manuscript","review","task"]

def new_store(project_id:str="PROJECT-001")->dict[str,Any]:
    return {"project_id":project_id,"created_at":datetime.now(timezone.utc).isoformat(),"updated_at":datetime.now(timezone.utc).isoformat(),"entities":{t:[] for t in ENTITY_TYPES}}

def add_entity(store:dict[str,Any],entity_type:str,record:dict[str,Any])->dict[str,Any]:
    if entity_type not in ENTITY_TYPES: raise ValueError(f"Unsupported entity type: {entity_type}")
    item=dict(record); item.setdefault("id",f"{entity_type.upper()}-{len(store['entities'][entity_type])+1:05d}")
    store["entities"][entity_type].append(item); store["updated_at"]=datetime.now(timezone.utc).isoformat(); return item

def audit_store(store:dict[str,Any])->dict[str,Any]:
    counts={k:len(v) for k,v in store.get("entities",{}).items()}
    return {"project_id":store.get("project_id",""),"entity_counts":counts,"total_entities":sum(counts.values()),"updated_at":store.get("updated_at","")}

def export_json(store:dict[str,Any])->dict[str,Any]:
    return store
