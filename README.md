# ODyssey

## Research Proposal

### Project Summary
ODyssey, a Growth Curve Workbench is a local, notebook-first tool that lets lab users load growth curve datasets, analyze growth kinetics, and compare new results to prior runs without re-entering settings every time. The core innovation is a "project file" that persists run metadata, parsing rules, and analysis options, enabling a workflow similar to commercial qPCR software: open, adjust, re-run, and save.

### Problem Statement
Current growth curve workflows are fragmented: users must repeatedly specify file paths, sheet names, replicate mappings, and analysis windows. This leads to friction, inconsistent analysis, and poor reproducibility across runs and users. A lightweight, local system tailored to growth curves can reduce overhead while preserving flexibility.

### Objectives
- Build a reusable project format that stores dataset paths, parsing rules, and analysis settings.
- Provide interactive selection of datasets and grouping for visualization.
- Compute growth rates and doubling times with manual or auto-detected time windows.
- Compare new runs against saved runs for the same project.
- Flag questionable fits (e.g., low R2, negative slopes) to prompt review.

### Proposed Solution
The tool will be delivered as a Jupyter notebook with a simple UI (ipywidgets) and a local persistence layer (JSON + SQLite). Users can:
- Create or open a project file.
- Load Excel data and define sheet names, time columns, and well labels.
- Select strains/conditions to visualize and group them for plots.
- Choose growth-window detection (manual range or auto-fit by max R2).
- Save results and settings for future comparison.

### Methods
1. Data ingestion via `pandas.read_excel`.
2. Parsing of well labels into strain, condition, replicate.
3. Reshaping into long format and replicate aggregation.
4. Growth rate estimation by fitting log(OD) vs time.
5. Doubling time calculation as `ln(2) / mu`.
6. Results stored per project for comparison across runs.

### Expected Outcomes
- Reproducible, low-friction growth curve analysis.
- Faster turnaround for repeated experiments.
- Standardized reporting with consistent plots and tables.

### Scope and Deliverables
- A project file format (`.growthproj`) and local storage.
- A notebook UI that supports data selection and grouping.
- Growth-rate and doubling-time outputs with fit diagnostics.
- Comparison view between historical and new runs.

### Risks and Mitigations
- **Risk:** heterogeneous labeling in Excel files.
  **Mitigation:** user-configurable parsing rules and previews.
- **Risk:** overfitting on noisy data.
  **Mitigation:** R2 thresholds and manual override.

### Tech Stack
- Python 3.9+
- pandas, numpy, scipy
- matplotlib, seaborn
- openpyxl, ipywidgets

### Timeline (Proposed)
- Week 1: define project schema, ingestion, parsing.
- Week 2: analysis methods (growth rate, window selection).
- Week 3-4: UI, persistence, comparisons, reporting.
