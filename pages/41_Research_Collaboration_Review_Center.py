from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from src.scimantra.cloud import configured, client, current_user, list_artifacts, list_projects

st.title("🤝 Research Collaboration & Review Center")
st.caption("Coordinate researcher, supervisor, co-author, and reviewer feedback around the project's saved evidence.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to use collaboration tools.")
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
    st.error(f"Could not load project evidence: {exc}")
    st.stop()

# Review records are intentionally stored as project artifacts so this module works
# with the existing Vault schema without silently creating an untracked database.
def save_review_record(payload: dict):
    raw = json.dumps(payload, indent=2, default=str).encode("utf-8")
    try:
        from src.scimantra.cloud import create_artifact, upload_project_file
        filename = f"review_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        path = upload_project_file(supa, user.id, project["id"], filename, raw, "application/json")
        return create_artifact(
            supa, user.id, project["id"], filename, "review_record", path,
            "application/json", len(raw), __import__("hashlib").sha256(raw).hexdigest(),
            "Research Collaboration & Review Center", payload
        )
    except Exception as exc:
        return exc

review_artifacts = [a for a in artifacts if str(a.get("artifact_type", "")).lower() in {"review_record", "review", "collaboration_review"} or "review_record" in str(a.get("source_tool", "")).lower()]

st.subheader("Review status")
status_values = {"Draft", "In review", "Changes requested", "Approved", "Closed"}
status_counts = {s: 0 for s in status_values}
for a in review_artifacts:
    p = a.get("provenance_json", {})
    if isinstance(p, str):
        try: p = json.loads(p)
        except Exception: p = {}
    s = p.get("status", "Draft") if isinstance(p, dict) else "Draft"
    if s not in status_counts: s = "Draft"
    status_counts[s] += 1

cols = st.columns(5)
for col, status in zip(cols, ["Draft", "In review", "Changes requested", "Approved", "Closed"]):
    col.metric(status, status_counts[status])

st.subheader("Create review record")
with st.form("review_form"):
    reviewer = st.text_input("Reviewer / collaborator", placeholder="Supervisor, co-author, reviewer name")
    role = st.selectbox("Role", ["Supervisor", "Co-author", "Research collaborator", "Internal reviewer", "External reviewer"])
    target = st.selectbox("Review target", ["Dataset", "Quality audit", "Statistical validation", "Evidence passport", "Figures", "Manuscript", "Submission package", "Whole project"])
    status = st.selectbox("Status", ["Draft", "In review", "Changes requested", "Approved", "Closed"])
    decision = st.text_area("Review decision / key feedback", placeholder="Record concise, actionable feedback.")
    action = st.text_area("Required action", placeholder="What should be changed, checked, or approved?")
    submitted = st.form_submit_button("💾 Save review record")

if submitted:
    if not reviewer.strip() or not decision.strip():
        st.error("Reviewer name and review decision / feedback are required.")
    else:
        payload = {
            "reviewer": reviewer.strip(), "role": role, "target": target,
            "status": status, "decision": decision.strip(), "required_action": action.strip(),
            "recorded_by": user.id, "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        result = save_review_record(payload)
        if isinstance(result, Exception):
            st.error(f"Could not save review record: {result}")
        else:
            st.success("Review record saved to the project Vault. Refresh the page to see it in the ledger.")

st.subheader("Review ledger")
if review_artifacts:
    rows = []
    for a in review_artifacts:
        p = a.get("provenance_json", {})
        if isinstance(p, str):
            try: p = json.loads(p)
            except Exception: p = {}
        p = p if isinstance(p, dict) else {}
        rows.append({
            "Reviewer": p.get("reviewer", "Not recorded"),
            "Role": p.get("role", "Not recorded"),
            "Target": p.get("target", "Not recorded"),
            "Status": p.get("status", "Draft"),
            "Recorded": p.get("recorded_at", a.get("created_at", "")),
            "Artifact": a.get("name", ""),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)
    st.download_button("⬇️ Export review ledger", df.to_csv(index=False).encode("utf-8"), "research_review_ledger.csv", "text/csv")
    for a, row in zip(review_artifacts, rows):
        with st.expander(f"{row['Status']} · {row['Reviewer']} · {row['Target']}"):
            p = a.get("provenance_json", {})
            if isinstance(p, str):
                try: p = json.loads(p)
                except Exception: p = {}
            st.json(p if isinstance(p, dict) else {})
else:
    st.info("No review records have been saved yet.")

st.subheader("Collaboration checklist")
items = [
    "Experimental-unit definition has been reviewed.",
    "Replicate structure and statistical unit have been reviewed.",
    "Quality-control decisions have been documented.",
    "Primary figures have been checked against the analyzed dataset.",
    "Major manuscript claims have an evidence trail.",
    "Submission declarations and journal requirements have been reviewed.",
]
for item in items:
    st.checkbox(item, key="collab_" + str(abs(hash(item))))

st.divider()
st.caption("Collaboration safeguard: review records document human feedback and workflow status. An 'Approved' review does not constitute independent scientific validation or guarantee publication acceptance.")
