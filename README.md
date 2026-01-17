# ODyssey - Growth Curve Workbench

## Research Proposal

### Project Summary
ODyssey - Growth Curve Workbench is a local, student-friendly web app that lets lab users load growth curve datasets, analyze growth kinetics, and re-run analyses without repeatedly re-entering settings. The core innovation is a reusable config file that stores parsing rules and analysis options so users can drop in a new Excel file and go straight to results.

### Problem Statement
Current growth curve workflows are fragmented: users must repeatedly specify file paths, sheet names, replicate mappings, and analysis windows. This leads to friction, inconsistent analysis, and poor reproducibility across runs and users. A lightweight, local system tailored to growth curves can reduce overhead while preserving flexibility.

### Objectives
- Build a reusable project format that stores dataset paths, parsing rules, and analysis settings.
- Provide interactive selection of datasets and grouping for visualization.
- Compute growth rates and doubling times with manual or auto-detected time windows.
- Compare new runs against saved runs for the same project.
- Flag questionable fits (e.g., low R2, negative slopes) to prompt review.

### Proposed Solution
The tool will be delivered as a local web app (Streamlit) with a streamlined UI and a reusable JSON config file. Users can:
- Upload Excel data and confirm auto-detected sheet/time/columns.
- Save a config file that captures selections and analysis settings.
- Reuse the config to skip setup on future runs.
- Run analysis and download results as CSV.

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
- pandas, numpy
- openpyxl
- streamlit


## Quick Start (Local Web App)

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```

3. Upload an Excel file, optionally upload a saved config, and run the analysis.

Use "Generate config" to download a config file for future runs.
