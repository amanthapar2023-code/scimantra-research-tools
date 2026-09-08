from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

st.set_page_config(page_title="H₂S Journal Submission Packager", page_icon="📦", layout="wide")
st.title("📦 H₂S Journal Submission Packager")
st.caption("Turn the completed research evidence into a journal-submission checklist and structured manuscript package without inventing citations or experimental claims.")

st.markdown("### 1. Submission profile")
journal = st.text_input("Target journal", "")
article_type = st.selectbox("Article type", ["Original Research Article", "Short Communication", "Research Note", "Thesis Chapter", "Preprint"])
title = st.text_input("Final manuscript title", "H₂S removal performance in a biological treatment system")
author_line = st.text_input("Authors", "")
corresponding = st.text_input("Corresponding author", "")
keywords = st.text_input("Keywords", "H₂S; hydrogen sulfide; biological treatment; bioreactor; gas treatment")

st.markdown("### 2. Manuscript completeness")
items = [
    ("Title finalized", bool(title.strip())),
    ("Authors and affiliations verified", bool(author_line.strip())),
    ("Corresponding author details verified", bool(corresponding.strip())),
    ("Abstract finalized", False),
    ("Introduction with verified literature", False),
    ("Materials and Methods complete", False),
    ("Results checked against raw data", False),
    ("Discussion supported by evidence", False),
    ("Figures numbered and cited", False),
    ("Tables numbered and cited", False),
    ("References verified", False),
    ("Ethics / biosafety / declarations checked", False),
    ("Data availability statement prepared", False),
    ("Funding statement prepared", False),
    ("Conflict of interest statement prepared", False),
]
state = {}
for label, default in items:
    state[label] = st.checkbox(label, value=default)

completed = sum(state.values())
progress = completed / len(items)
st.progress(progress, text=f"Submission readiness: {completed}/{len(items)} checklist items complete")

st.markdown("### 3. Required declarations")
data_availability = st.text_area("Data availability", "The underlying experimental dataset and analysis evidence should be deposited in an appropriate repository or made available from the corresponding author, subject to institutional and journal requirements.")
funding = st.text_area("Funding", "Add verified funding information or state that no external funding was received, as appropriate.")
coi = st.text_area("Conflict of interest", "Add the authors' verified conflict-of-interest declaration.")
ethics = st.text_area("Ethics / biosafety / compliance", "Add the verified institutional, biosafety and regulatory statements applicable to the study.")
code = st.text_area("Code / software availability", "SciMantra analysis outputs should be accompanied by the analysis settings and evidence passport where appropriate.")

st.markdown("### 4. Reviewer-proof evidence checklist")
review_checks = [
    "Raw-data source is preserved",
    "Measurement units are documented",
    "Experimental unit and replicate definition are explicit",
    "Inclusion/exclusion rules are documented",
    "Calculation formulas are stated",
    "Statistical assumptions are checked",
    "Multiple-comparison strategy is justified where applicable",
    "Error bars are defined in every figure",
    "n values are visible or stated",
    "Negative/zero/invalid measurements are explained",
    "Optimization claims are independently confirmed",
    "Literature claims have real references",
]
review_state = {x: st.checkbox(x, key="review_" + x) for x in review_checks}
review_done = sum(review_state.values())

st.markdown("### 5. Submission package manifest")n
manifest = {
    "package_version": "1.0",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "journal": journal,
    "article_type": article_type,
    "title": title,
    "authors": author_line,
    "corresponding_author": corresponding,
    "keywords": [x.strip() for x in keywords.split(";") if x.strip()],
    "manuscript_checklist": state,
    "reviewer_evidence_checklist": review_state,
    "readiness_percent": round(progress * 100, 1),
    "review_evidence_percent": round(review_done / len(review_checks) * 100, 1),
    "declarations": {
        "data_availability": data_availability,
        "funding": funding,
        "conflict_of_interest": coi,
        "ethics_biosafety": ethics,
        "code_availability": code,
    },
}

st.json(manifest)

st.markdown("### 6. Cover-letter draft")
cover = f"Dear Editor,\n\nPlease consider our {article_type.lower()} entitled '{title}' for consideration in {journal or '[Target Journal]'}. The manuscript reports experimentally derived H₂S treatment performance and presents transparent quantitative analysis of the underlying observations.\n\nThe work is accompanied by a structured evidence and reproducibility record. All scientific claims, citations, declarations and journal-specific requirements should be independently verified by the authors before submission.\n\nSincerely,\n{corresponding or '[Corresponding Author]'}"
st.text_area("Cover letter", cover, height=260)

st.markdown("### 7. Submission manifest download")
manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
readme = f"# H₂S Journal Submission Package\n\nJournal: {journal or '[Target Journal]'}\nArticle type: {article_type}\nTitle: {title}\n\n## Readiness\nManuscript checklist: {completed}/{len(items)}\nReviewer evidence checklist: {review_done}/{len(review_checks)}\n\n## Before submission\n- Verify every quantitative result against the raw dataset.\n- Verify all references and journal formatting requirements.\n- Confirm author approval and declarations.\n- Upload figures at the journal's required resolution and format.\n- Do not claim causality or a validated optimum without appropriate experimental evidence.\n"
col1, col2 = st.columns(2)
with col1:
    st.download_button("⬇️ Submission manifest JSON", manifest_json, "h2s_submission_manifest.json", "application/json", width="stretch")
with col2:
    st.download_button("⬇️ Submission README", readme.encode("utf-8"), "h2s_submission_readme.md", "text/markdown", width="stretch")

st.warning("This tool organizes and audits submission readiness. It does not certify that a manuscript meets a journal's current author instructions, and it does not fabricate references, declarations, affiliations or experimental facts.")
