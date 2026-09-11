"""Research impact and reuse planning engine."""
from __future__ import annotations
from typing import Any

OUTPUT_TYPES=["Follow-up paper","New experiment","Dataset","Reusable method","Patent / IP review","Review / meta-analysis","Application / translation","Collaboration","New research question","Figure / data / code reuse"]
PRIORITIES=["High","Medium","Low"]

def audit(items:list[dict[str,Any]])->dict[str,Any]:
    return {"total":len(items),"high":sum(x.get("priority")=="High" for x in items),"planned":sum(bool(x.get("next_step","").strip()) for x in items),"unplanned":sum(not x.get("next_step","").strip() for x in items)}

def next_actions(items:list[dict[str,Any]])->list[str]:
    return [f"Define next step for {x.get('title','output')}" for x in items if not x.get("next_step","").strip()][:10]
