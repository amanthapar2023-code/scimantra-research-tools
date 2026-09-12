"""Phase 111: unified scientific readiness scorecard.

Fuses explicit audit signals from the Research OS into one transparent
scorecard. It never runs scientific analyses or decides whether a study is
scientifically true.
"""
from __future__ import annotations
from typing import Any

DOMAINS = ["Evidence sufficiency", "Claim stress test", "Causal validity", "Bias / error", "Statistical readiness", "Robustness", "Reproducibility", "Generalizability", "Mechanism consistency", "Novelty / prior art", "Reviewer risk"]
LEVELS = ["Not assessed", "Strong", "Adequate", "Needs work", "Critical gap"]
WEIGHTS = {"Strong": 3, "Adequate": 2, "Needs work": 1, "Critical gap": 0, "Not assessed": 0}

def score(signals: list[dict[str, Any]]) -> dict[str, Any]:
    by = {str(x.get("domain") or x.get("signal")): x.get("level", "Not assessed") for x in signals}
    rows=[]
    for domain in DOMAINS:
        level=by.get(domain,"Not assessed")
        rows.append({"domain":domain,"level":level,"weight":WEIGHTS.get(level,0)})
    assessed=sum(r["level"] != "Not assessed" for r in rows)
    total=sum(r["weight"] for r in rows)
    max_score=3*len(rows)
    return {"score":round(100*total/max_score,1) if max_score else 0.0,"assessed":assessed,"total_domains":len(rows),"critical":sum(r["level"]=="Critical gap" for r in rows),"needs_work":sum(r["level"]=="Needs work" for r in rows),"rows":rows}

def readiness(result: dict[str, Any]) -> str:
    if result.get("critical",0)>0: return "Critical gaps"
    if result.get("assessed",0)<result.get("total_domains",0): return "Incomplete assessment"
    if result.get("needs_work",0)>0: return "Needs work"
    if result.get("score",0)>=80: return "Strong readiness"
    if result.get("score",0)>=60: return "Adequate readiness"
    return "Needs work"

def actions(result: dict[str, Any]) -> list[str]:
    out=[]
    for r in result.get("rows",[]):
        if r["level"]=="Critical gap": out.append(f"Resolve critical gap: {r['domain']}")
        elif r["level"]=="Needs work": out.append(f"Improve: {r['domain']}")
        elif r["level"]=="Not assessed": out.append(f"Assess: {r['domain']}")
    return out

def export_markdown(result: dict[str, Any]) -> str:
    lines=["# SciMantra Scientific Readiness Scorecard","",f"**Score:** {result.get('score',0)} / 100",f"**Readiness:** {readiness(result)}","","| Domain | Level | Weight |","|---|---|---:|"]
    lines += [f"| {r['domain']} | {r['level']} | {r['weight']} |" for r in result.get("rows",[])]
    return "\n".join(lines)
