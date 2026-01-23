# ODyssey

## Project Proposal

### Project Summary
ODyssey - Growth Curve Workbench is a web app for analyzing plate reader growth curves. It turns
raw Excel files into reusable analyses with clear fit windows, QC flags, and exportable plots. A
config-first workflow lets users rerun the same analysis on new files without re-entering settings.

Website: https://srriash.github.io/ODyssey-Growth-curve-workbench/

### Problem Statement
Growth curve workflows often require repeated setup: selecting sheets, time columns, replicate
mappings, and fit windows for every run. This slows iteration, creates inconsistency, and makes
comparisons across runs harder to trust.

### Objectives
- Provide a guided UI for uploading Excel files and mapping treatments/replicates.
- Fit growth rates and doubling times from exponential windows with QC flags.
- Compute AUC using full range, fit window, or a custom range.
- Compare runs using exported results without re-running analysis.
- Export results, plots, and reports in a single bundle.
- Persist analysis settings with reusable JSON configs.

### Solution
Deliver a Streamlit app that integrates data ingestion, analysis, visualization, and exports:
- Upload Excel data and optionally load a saved config.
- Preview curves and set the fit window (auto or manual).
- Run analysis and generate plots and tables.
- Export results, plots, and a PDF report as a zip.
- Reuse configs to repeat the same analysis on new runs.

### Methods
1. Read Excel files and parse time columns into numeric units.
2. Apply optional blank normalization using selected blank columns.
3. Convert wide data to long format by treatment and replicate.
4. Fit a linear model to log(OD) vs time within selected windows to estimate growth rate.
5. Compute doubling time and AUC with unit conversions.
6. Generate plots and QC flags for low R^2 or non-positive growth rates.
7. Export results, plots, and configs for reuse and comparison.

### Scope and Deliverables
- Streamlit analysis app with reusable configs.
- Overlay, small-multiple, and comparison plots.
- CSV results, long-format data, HTML/PNG plots, and PDF reports.
- Zip exports suitable for cross-run comparisons.

### Tech Stack
- Python 3.9+
- pandas, numpy
- plotly
- streamlit
- reportlab

## Quick Start (Local)
Run the app locally from the repo root:
```bash
pip install -r requirements.txt
streamlit run app.py
```
