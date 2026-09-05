# SciMantra Research Tools — Platform Architecture

## Purpose

SciMantra Research Tools is a practical scientific computing platform for students, researchers, educators and science professionals. The public SciMantra website remains the content and discovery layer; this repository is the application and research-computation layer.

## Current application areas

- Laboratory calculators
- Statistics
- Environmental biotechnology calculations
- CSV/Excel data analysis
- Advanced experimental data analysis
- Research utilities
- Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA)

## Architecture direction

The application should evolve toward clear feature modules rather than one increasingly large `app.py` file.

```text
SciMantra Research Tools
│
├── Dashboard
├── Laboratory
│   ├── Concentration & solution calculations
│   ├── Microbiology calculations
│   └── Growth / wastewater calculations
├── Statistics
│   ├── Descriptive statistics
│   ├── Hypothesis testing
│   ├── Correlation
│   └── Regression
├── Data Analyzer
│   ├── CSV / Excel import
│   ├── Data validation
│   ├── Replicate handling
│   ├── Summary tables
│   └── Interactive visualization
├── Advanced Research Analysis
│   ├── H₂S reactor analysis
│   ├── Kinetics
│   ├── Controls
│   ├── Sulfur transformation
│   ├── Stability
│   └── Publication figures
├── Research Utilities
│   ├── Standard curves
│   ├── Experimental design
│   └── Manuscript / research checklists
└── Sustainability
    ├── TEA
    └── LCA
```

## Design principles

1. Preserve scientific traceability: distinguish raw observations, reported values, preliminary observations and planned work.
2. Prefer reusable calculation functions over duplicated formulas.
3. Validate inputs before calculating results.
4. Show units, assumptions and interpretation alongside numerical outputs.
5. Keep downloadable outputs reproducible and clearly labelled.
6. Use the SciMantra visual language consistently: dark blue `#123f72`, green `#2d8a5b`, body text `#40505f`, pale backgrounds and light borders.
7. Keep research-specific knowledge separate from generic calculation logic.
8. Avoid silently reconciling conflicting research values; flag them for review.
9. Add new modules without breaking existing research tools.

## Deployment

The repository is designed for Streamlit Community Cloud. The application entry point is `app.py`. GitHub is the source of truth for application code and version history.

## Roadmap

### Phase 1 — foundation
- Document architecture and conventions.
- Keep the current working application intact.
- Establish a predictable module layout.

### Phase 2 — modularization
- Move reusable calculations into dedicated modules.
- Separate UI routing from scientific calculations.
- Centralize validation, units and export helpers.

### Phase 3 — research-grade workflows
- Strengthen replicate-aware analysis.
- Add DOE/RSM planning.
- Add stability and scale-up analysis.
- Improve publication-ready export.
- Add research conflict/data-quality checks.

### Phase 4 — SciMantra platform
- Connect WordPress landing pages to individual tools.
- Add user-friendly documentation and examples.
- Expand laboratory, biotechnology and environmental calculators.
- Build a coherent research workflow from experimental design through analysis and reporting.
