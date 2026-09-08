"""SciMantra Research Intelligence Engine - first title-to-research prototype.

No fabricated experimental results are produced. Literature evidence is fetched from
Crossref when available; all generated scientific statements are framed as hypotheses,
questions, or candidate directions rather than facts.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
import json
from collections import Counter
from typing import Any

STOPWORDS = {
    "the", "and", "for", "with", "using", "use", "of", "in", "on", "to", "a", "an",
    "from", "by", "via", "based", "study", "studies", "development", "investigation",
    "analysis", "effect", "effects", "novel", "approach", "method", "methods", "towards",
    "through", "into", "over", "under", "during", "their", "its", "this", "that", "is",
    "are", "was", "were", "as", "at", "or", "be", "been", "being", "model", "models",
}


def extract_terms(title: str, limit: int = 12) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}|[A-Za-z0-9]+(?:₂|₃|₄|₅|₆|₇|₈|₉|₀)+", title)
    clean = [w.lower() for w in words if w.lower() not in STOPWORDS]
    counts = Counter(clean)
    return [w for w, _ in counts.most_common(limit)]


def infer_components(title: str) -> dict[str, str]:
    t = title.strip()
    terms = extract_terms(t)
    lower = t.lower()
    component = {
        "Problem / system": "the scientific problem described by the title",
        "Technology / approach": "the principal method or technology",
        "Target / material": "the organism, material, sample, or target under study",
        "Outcome": "the measurable outcome or response",
        "Context": "the application or experimental context",
    }
    # Lightweight interpretable heuristics; users can edit these later.
    tech_words = [x for x in ["biosensor", "sensor", "nanoparticle", "machine learning", "ai", "reactor", "membrane", "adsorption", "bioremediation", "fermentation", "spectroscopy", "chromatography"] if x in lower]
    outcome_words = [x for x in ["removal", "detection", "yield", "growth", "efficiency", "performance", "degradation", "production", "sensitivity", "accuracy", "toxicity"] if x in lower]
    if terms:
        component["Problem / system"] = "research system involving " + ", ".join(terms[:4])
    if tech_words:
        component["Technology / approach"] = ", ".join(tech_words)
    elif len(terms) >= 2:
        component["Technology / approach"] = terms[0]
    if len(terms) >= 3:
        component["Target / material"] = terms[1]
    if outcome_words:
        component["Outcome"] = ", ".join(outcome_words)
    if "wastewater" in lower or "waste water" in lower:
        component["Context"] = "wastewater / environmental application"
    elif "soil" in lower:
        component["Context"] = "soil / environmental application"
    elif "clinical" in lower or "patient" in lower:
        component["Context"] = "clinical / biomedical application"
    else:
        component["Context"] = "the application context implied by the title"
    return component


def generate_blueprint(title: str) -> dict[str, Any]:
    terms = extract_terms(title)
    c = infer_components(title)
    topic = ", ".join(terms[:6]) if terms else title
    questions = [
        f"What is the relationship between the main intervention/approach and the measured outcome in {topic}?",
        f"Which experimental or operational variables most strongly influence the outcome?",
        "Does the proposed approach outperform an appropriate control or established benchmark?",
        "What mechanism could explain the observed response, and what evidence would distinguish competing explanations?",
        "How robust is the finding across replicates, conditions, or realistic application settings?",
    ]
    objectives = [
        f"Characterize the baseline state of the system described by the title.",
        "Evaluate the proposed approach under defined experimental conditions.",
        "Quantify the principal response variables with appropriate replication and uncertainty reporting.",
        "Compare the proposed approach with a defensible control or benchmark.",
        "Identify the variables and mechanisms that explain variation in the response.",
    ]
    hypotheses = [
        "H1: The proposed approach produces a measurable change in the primary outcome relative to the control.",
        "H2: The magnitude of the response depends on one or more controllable experimental variables.",
        "H3: The observed response remains robust after accounting for replication and relevant confounders.",
    ]
    gap = [
        "Interaction gap: determine whether combinations of variables have been tested together rather than independently.",
        "Mechanism gap: distinguish the proposed mechanism from plausible alternative explanations.",
        "Translation gap: test whether laboratory-scale findings remain valid under realistic operating conditions.",
        "Evidence gap: quantify uncertainty, replication, and effect size rather than relying only on statistical significance.",
    ]
    method = [
        "Define primary and secondary outcomes before data collection.",
        "Pre-specify experimental groups, controls, replicates, inclusion/exclusion rules, and sampling schedule.",
        "Record raw observations and metadata so every reported value can be traced to an experiment.",
        "Use effect sizes and confidence intervals alongside p-values where appropriate.",
        "Document deviations from the planned protocol and assess their potential influence.",
    ]
    return {"terms": terms, "components": c, "questions": questions, "objectives": objectives, "hypotheses": hypotheses, "gap": gap, "method": method}


def crossref_search(title: str, rows: int = 12) -> list[dict[str, Any]]:
    """Search Crossref works using the title as a phrase. Returns metadata only."""
    params = urllib.parse.urlencode({"query.title": title, "rows": rows, "select": "DOI,title,author,published,container-title,type,URL"})
    url = "https://api.crossref.org/works?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "SciMantra/ResearchIntelligence/0.1 (mailto:research@scimantra.com)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = []
    for item in data.get("message", {}).get("items", []):
        titles = item.get("title") or []
        title_text = titles[0] if titles else "Untitled"
        authors = item.get("author") or []
        author = ", ".join((a.get("family") or a.get("name") or "") for a in authors[:3]).strip(", ")
        date = item.get("published", {}).get("date-parts", [[None]])[0]
        year = date[0] if date and date[0] else ""
        items.append({"Title": title_text, "Year": year, "Authors": author, "Journal": (item.get("container-title") or [""])[0], "DOI": item.get("DOI", ""), "Type": item.get("type", ""), "URL": item.get("URL", "")})
    return items


def title_similarity(a: str, b: str) -> float:
    sa, sb = set(extract_terms(a, 20)), set(extract_terms(b, 20))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def novelty_report(title: str, papers: list[dict[str, Any]]) -> dict[str, Any]:
    scored = sorted(((title_similarity(title, p.get("Title", "")), p) for p in papers), reverse=True, key=lambda x: x[0])
    high = [p for s, p in scored if s >= 0.55]
    medium = [p for s, p in scored if 0.35 <= s < 0.55]
    if high:
        level = "HIGH COLLISION RISK"
        explanation = "Several retrieved titles share a large fraction of the core concepts. Inspect these papers before claiming novelty."
    elif medium:
        level = "MODERATE COLLISION RISK"
        explanation = "Related work is visible, but the title alone does not establish that the proposed combination is already done."
    else:
        level = "LOW TITLE-LEVEL COLLISION"
        explanation = "Few close title matches were retrieved. This is not proof of novelty; broader concept and citation-network checks are still required."
    return {"level": level, "explanation": explanation, "high": high[:5], "medium": medium[:5]}


def build_matrix(papers: list[dict[str, Any]], title: str) -> list[dict[str, Any]]:
    terms = set(extract_terms(title, 20))
    matrix = []
    for p in papers:
        pt = set(extract_terms(p.get("Title", ""), 20))
        overlap = sorted(terms & pt)
        matrix.append({**p, "Concept overlap": len(overlap), "Shared concepts": ", ".join(overlap[:8]), "Evidence status": "Metadata only — full text required for claim-level extraction"})
    return matrix
