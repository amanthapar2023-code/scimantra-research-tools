from typing import Dict, List

DESIGN_OPTIONS = {
    "Comparator": ["No comparator specified", "Matched/reference comparator", "Active comparator", "Vehicle/sham/baseline control"],
    "Replication": ["Technical repeats only", "Independent biological/experimental replicates", "Independent replicates with blocked/batched structure"],
    "Allocation": ["No allocation rule", "Randomized allocation", "Randomized blocked/stratified allocation"],
    "Blinding": ["Open", "Single blind", "Double blind / blinded assessment"],
    "Measurement": ["Single measurement", "Replicate measurement + QC", "Replicate measurement + QC + predefined acceptance criteria"],
    "Analysis": ["Post-hoc analysis choices", "Pre-specified primary analysis", "Pre-specified primary analysis + sensitivity/robustness analyses"],
    "Reproducibility": ["Basic notes", "Protocol + data provenance", "Versioned protocol + provenance + code/settings + deviations"],
}

BENEFIT = {
    "Comparator": [0, 12, 15, 14], "Replication": [0, 18, 20], "Allocation": [0, 14, 17],
    "Blinding": [0, 7, 9], "Measurement": [0, 10, 13], "Analysis": [0, 13, 17], "Reproducibility": [0, 10, 15],
}


def score_option(category: str, index: int) -> Dict[str, object]:
    labels = DESIGN_OPTIONS[category]
    index = max(0, min(index, len(labels) - 1))
    return {"Category": category, "Selected design": labels[index], "Validity/robustness contribution": BENEFIT[category][index], "Trade-off": "Higher implementation burden" if index == len(labels) - 1 else "Moderate implementation burden" if index > 0 else "Low burden but weak protection"}


def optimize_design(selections: Dict[str, int]) -> List[Dict[str, object]]:
    rows = [score_option(cat, selections.get(cat, 0)) for cat in DESIGN_OPTIONS]
    return rows


def improvement_actions(selections: Dict[str, int]) -> List[Dict[str, object]]:
    rows = []
    for cat, options in DESIGN_OPTIONS.items():
        current = selections.get(cat, 0)
        if current < len(options) - 1:
            delta = BENEFIT[cat][current + 1] - BENEFIT[cat][current]
            rows.append({"Category": cat, "Current": options[current], "Next improvement": options[current + 1], "Estimated robustness gain": delta, "Reason": "Stronger protection against bias, measurement error, or analytic ambiguity."})
    return sorted(rows, key=lambda x: x["Estimated robustness gain"], reverse=True)


def design_score(selections: Dict[str, int]) -> float:
    total = sum(BENEFIT[c][max(0, min(i, len(BENEFIT[c])-1))] for c, i in selections.items() if c in BENEFIT)
    maximum = sum(max(v) for v in BENEFIT.values())
    return round(100 * total / maximum, 1) if maximum else 0.0


def export_optimizer(selections: Dict[str, int], rows: List[Dict], actions: List[Dict]) -> str:
    lines = ["# SciMantra Experimental Design Optimizer", "", f"Design robustness index: {design_score(selections)}%", "", "## Selected design"]
    lines += [f"- **{r['Category']}**: {r['Selected design']} — contribution {r['Validity/robustness contribution']}" for r in rows]
    lines += ["", "## Highest-value improvements"]
    lines += [f"- **{a['Category']}**: {a['Current']} → {a['Next improvement']} (+{a['Estimated robustness gain']}) — {a['Reason']}" for a in actions]
    lines.append("\n> Scores are structured planning heuristics, not statistical guarantees or field-specific power calculations.")
    return "\n".join(lines)
