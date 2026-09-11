"""Cross-project research knowledge index and reusable insight engine."""
from __future__ import annotations
from typing import Any

KNOWLEDGE_TYPES=["Method","Evidence","Finding","Research gap","Hypothesis","Dataset","Failed approach","Research question"]

def new_index()->dict[str,Any]: return {"records":[]}

def add_record(index:dict[str,Any],project_id:str,kind:str,title:str,summary:str,tags:str="")->dict[str,Any]:
    r={"project_id":project_id,"type":kind,"title":title,"summary":summary,"tags":tags}; index.setdefault("records",[]).append(r); return r

def search(index:dict[str,Any],query:str)->list[dict[str,Any]]:
    q=query.lower().strip()
    if not q:return list(index.get("records",[]))
    return [r for r in index.get("records",[]) if q in " ".join(str(r.get(k,"")) for k in ("title","summary","tags","type","project_id")).lower()]

def reusable(index:dict[str,Any])->list[dict[str,Any]]:
    return [r for r in index.get("records",[]) if r.get("type") in {"Method","Dataset","Finding","Failed approach","Research gap"}]
