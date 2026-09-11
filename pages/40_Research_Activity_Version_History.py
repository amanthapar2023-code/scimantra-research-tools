from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from src.scimantra.cloud import configured, client, current_user, list_artifacts, list_projects

st.title("🕒 Research Activity & Version History")
st.caption("A chronological project log built from saved research artifacts and their provenance.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to view project history.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("Create a project in Cloud Research Workspace first.")
    st.stop()

names = [p.get("name", "Untitled") for p in projects]
selected = st.selectbox("Research project", names)
project = next(p for p in projects if p.get("name") == selected)

try:
    artifacts = list_artifacts(supa, project["id"])
except Exception as exc:
    st.error(f"Could not load project history: {exc}")
    st.stop()


def prov(a):
    p = a.get("provenance_json", {})
    if isinstance(p, str):
        try: p = json.loads(p)
        except Exception: p = {}
    return p if isinstance(p, dict) else {}


def stage(a):
    h = " ".join([str(a.get("name", "")), str(a.get("artifact_type", "")), str(a.get("source_tool", "")), json.dumps(prov(a), default=str)]).lower()
    rules = [
        ("Dataset", ["dataset", "raw data"]),
        ("Quality", ["quality audit", "data quality", "quality_gate"]),
        ("Statistics", ["statistical validation", "replicate-aware"]),
        ("Evidence", ["evidence passport", "reproducibility evidence", "passport"]),
        ("Figures", ["publication figure", "figure engine", "figure set"]),
        ("Manuscript", ["manuscript studio", "complete manuscript", "manuscript"]),
        ("Submission", ["submission package", "submission packager"]),
        ("Package", ["research package", "study package", "study packager"]),
    ]
    return next((s for s, keys in rules if any(k in h for k in keys)), "Other")


def parsed_time(a):
    raw = a.get("created_at")
    if not raw: return None
    try:
        return pd.to_datetime(raw, utc=True)
    except Exception:
        return None

for a in artifacts:
    a["_stage"] = stage(a)
    a["_time"] = parsed_time(a)

artifacts.sort(key=lambda x: x.get("_time") or pd.Timestamp.min.tz_localize("UTC"), reverse=True)

st.subheader("Project activity")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Recorded events", len(artifacts))
c2.metric("Research stages", len(set(a["_stage"] for a in artifacts)))
c3.metric("Source tools", len(set(a.get("source_tool") or "Not recorded" for a in artifacts)))
c4.metric("Latest event", artifacts[0].get("created_at", "—")[:10] if artifacts else "—")

stage_filter = st.selectbox("Stage filter", ["All"] + sorted(set(a["_stage"] for a in artifacts)))
filtered = artifacts if stage_filter == "All" else [a for a in artifacts if a["_stage"] == stage_filter]

st.subheader("Chronological history")
if not filtered:
    st.info("No activity matches this filter.")
else:
    for i, a in enumerate(filtered):
        icon = {"Dataset":"📊","Quality":"🔎","Statistics":"🧮","Evidence":"🛡️","Figures":"📈","Manuscript":"📝","Submission":"📦","Package":"🗃️"}.get(a["_stage"], "•")
        title = f"{icon} {a.get('name', 'Unnamed artifact')}"
        with st.expander(f"{title}  ·  {a['_stage']}  ·  {a.get('created_at', 'time not recorded')}", expanded=i == 0):
            st.write(f"**Source tool:** {a.get('source_tool') or 'Not recorded'}")
            st.write(f"**Artifact type:** {a.get('artifact_type') or 'Not recorded'}")
            st.write(f"**Size:** {int(a.get('size_bytes') or 0):,} bytes")
            st.write(f"**SHA-256:** `{a.get('sha256') or 'Not recorded'}`")
            p = prov(a)
            if p:
                st.json(p, expanded=False)
            else:
                st.caption("No structured provenance recorded.")

st.subheader("Activity by stage")
counts = Counter(a["_stage"] for a in filtered)
summary = pd.DataFrame([{"Stage": k, "Events": v} for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))])
if not summary.empty:
    st.bar_chart(summary.set_index("Stage"), y="Events")

st.subheader("Exportable version history")
rows = []
for a in filtered:
    rows.append({
        "Project": project.get("name", ""),
        "Stage": a["_stage"],
        "Artifact": a.get("name", ""),
        "Source tool": a.get("source_tool", ""),
        "Artifact type": a.get("artifact_type", ""),
        "Created": a.get("created_at", ""),
        "Size bytes": a.get("size_bytes", 0),
        "SHA-256": a.get("sha256", ""),
    })
if rows:
    history = pd.DataFrame(rows)
    st.dataframe(history, width="stretch", hide_index=True)
    st.download_button("⬇️ Export version history CSV", history.to_csv(index=False).encode("utf-8"), "research_version_history.csv", "text/csv")

st.divider()
st.caption("Audit safeguard: this is a history of recorded project artifacts, not a complete reconstruction of every browser action or unsaved edit. It does not imply that an artifact version is scientifically superior merely because it is newer.")
