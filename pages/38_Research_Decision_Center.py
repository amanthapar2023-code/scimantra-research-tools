from __future__ import annotations

import json
import pandas as pd
import streamlit as st

from src.scimantra.cloud import configured, client, current_user, list_artifacts, list_projects

st.title("🎯 Research Decision Center")
st.caption("A structured final readiness review built from explicitly saved project evidence.")

if not configured(st.secrets):
    st.info("Cloud project mode is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets.")
    st.stop()

supa = client(st.secrets)
user = current_user(supa) if supa else None
if not user:
    st.warning("Sign in through the Cloud Account page to use the Research Decision Center.")
    st.stop()

projects = list_projects(supa, user.id)
if not projects:
    st.info("Create a research project first.")
    st.stop()

name = st.selectbox("Research project", [p.get("name", "Untitled") for p in projects])
project = next(p for p in projects if p.get("name") == name)

try:
    artifacts = list_artifacts(supa, project["id"])
except Exception as exc:
    st.error(f"Could not load evidence: {exc}")
    st.stop()


def prov(a):
    p = a.get("provenance_json", {})
    if isinstance(p, str):
        try: p = json.loads(p)
        except Exception: p = {}
    return p if isinstance(p, dict) else {}


def blob(a):
    return " ".join([str(a.get("name", "")), str(a.get("artifact_type", "")), str(a.get("source_tool", "")), json.dumps(prov(a), default=str)]).lower()

rules = [
    ("Dataset available", ["dataset", "raw data"]),
    ("Quality review recorded", ["quality audit", "data quality", "quality_gate"]),
    ("Statistical validation recorded", ["statistical validation", "replicate-aware"]),
    ("Evidence passport recorded", ["evidence passport", "reproducibility evidence", "passport"]),
    ("Publication figures recorded", ["publication figure", "figure engine", "figure set"]),
    ("Manuscript evidence recorded", ["manuscript studio", "complete manuscript", "manuscript"]),
    ("Submission package recorded", ["submission package", "submission packager"]),
    ("Reproducible research package recorded", ["research package", "study package", "study packager"]),
]

checks = []
for label, keys in rules:
    found = [a for a in artifacts if any(k in blob(a) for k in keys)]
    checks.append({"Check": label, "Status": "PASS" if found else "NEEDS WORK", "Artifacts": len(found)})

# Explicitly recorded readiness values only; no invented percentages.
def max_readiness(keyword):
    values = []
    for a in artifacts:
        for k, v in prov(a).items():
            if keyword in str(k).lower() and ("readiness" in str(k).lower() or "percent" in str(k).lower()):
                try:
                    x = float(v)
                    if x <= 1: x *= 100
                    if 0 <= x <= 100: values.append(x)
                except Exception: pass
    return max(values) if values else None

manuscript = max_readiness("manuscript")
submission = max_readiness("submission")

passed = sum(x["Status"] == "PASS" for x in checks)
coverage = passed / len(checks) if checks else 0

st.subheader("Decision")
if passed == len(checks):
    decision = "READY FOR FINAL REVIEW"
    st.success(f"🟢 {decision}")
elif passed >= 5:
    decision = "NEEDS FINAL EVIDENCE"
    st.warning(f"🟠 {decision}")
else:
    decision = "NOT READY"
    st.error(f"🔴 {decision}")

st.caption("This is a workflow readiness decision, not a claim that the science is correct or that a journal will accept the manuscript.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Evidence checks", f"{passed}/{len(checks)}")
c2.metric("Coverage", f"{coverage*100:.0f}%")
c3.metric("Manuscript", f"{manuscript:.0f}%" if manuscript is not None else "Not recorded")
c4.metric("Submission", f"{submission:.0f}%" if submission is not None else "Not recorded")

st.subheader("Readiness gate")
st.dataframe(pd.DataFrame(checks), width="stretch", hide_index=True)

missing = [x["Check"] for x in checks if x["Status"] != "PASS"]
if missing:
    st.subheader("Blocking / missing evidence")
    for item in missing:
        st.markdown(f"- ⬜ {item}")

st.subheader("Final review questions")
questions = [
    "Are experimental units and biological/technical replicates clearly defined?",
    "Was pseudoreplication avoided in inferential statistics?",
    "Were missing values, duplicates and outliers reviewed without unjustified deletion?",
    "Are statistical assumptions and effect sizes reported where appropriate?",
    "Do figures match the analyzed dataset and stated experimental design?",
    "Can every important numerical claim be traced to a saved evidence artifact?",
    "Has the manuscript been checked against the target journal's author instructions?",
]
answers = []
for q in questions:
    answers.append(st.checkbox(q, key="review_" + str(abs(hash(q)))))

review_complete = sum(answers) == len(questions)
st.divider()
if review_complete and not missing:
    st.success("🟢 Research workflow passes the recorded evidence gate and the manual final-review checklist.")
elif review_complete:
    st.warning("Manual review is complete, but saved evidence is still missing for one or more gates.")
else:
    st.info(f"Complete the remaining {len(questions) - sum(answers)} manual review question(s) before final sign-off.")

report = pd.DataFrame(checks)
report["Project"] = project.get("name", "")
report["Decision"] = decision
report["Manual review complete"] = review_complete
st.download_button("⬇️ Export Decision Report", report.to_csv(index=False).encode("utf-8"), "research_decision_report.csv", "text/csv")

st.divider()
st.caption("Scientific safeguard: the Center never manufactures readiness scores, statistical significance, or publication claims. It evaluates only recorded workflow evidence plus the user's manual checklist.")
