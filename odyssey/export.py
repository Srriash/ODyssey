import io
import json
import zipfile
from datetime import datetime, timezone
import sys

import plotly.io as pio

from odyssey.io_utils import _safe_filename

CONFIG_VERSION = 1


def _build_config(
    sheet_name,
    time_col,
    time_unit,
    time_window,
    fit_window_mode,
    min_points,
    blank_normalized,
    blank_cols,
    auc_mode,
    auc_window,
    auc_unit,
    notes,
    column_map,
    growth_rate_unit,
    doubling_time_unit,
    plot_groups,
    plot_mode,
    show_sd,
    charts_per_row,
    plot_labels,
):
    blank_col = blank_cols[0] if isinstance(blank_cols, list) and blank_cols else blank_cols
    return {
        "version": CONFIG_VERSION,
        "sheet_name": sheet_name,
        "time_col": time_col,
        "time_unit": time_unit,
        "time_window": time_window,
        "fit_window_mode": fit_window_mode,
        "min_points": min_points,
        "blank_normalized": blank_normalized,
        "blank_cols": blank_cols,
        "blank_col": blank_col,
        "auc_mode": auc_mode,
        "auc_window": auc_window,
        "auc_unit": auc_unit,
        "notes": notes,
        "column_map": column_map,
        "growth_rate_unit": growth_rate_unit,
        "doubling_time_unit": doubling_time_unit,
        "plot_groups": plot_groups,
        "plot_mode": plot_mode,
        "show_sd": show_sd,
        "charts_per_row": charts_per_row,
        "plot_labels": plot_labels,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_download_zip(
    *,
    results,
    analyses,
    plot_artifacts,
    config_payload,
    config_filename,
    download_results,
    download_long_df,
    download_config,
    download_plots,
    selected_plots,
    zip_filename,
    progress_cb=None,
):
    bundle = io.BytesIO()
    warnings = []
    timings = {}
    total_start = datetime.now().timestamp()
    selected_set = set(selected_plots)
    selected_plot_labels = [label for label, _ in plot_artifacts if not selected_set or label in selected_set]
    total_steps = 0
    total_steps += 1 if download_config else 0
    total_steps += 1 if download_results else 0
    total_steps += 1 if (download_long_df and analyses) else 0
    total_steps += len(selected_plot_labels) if download_plots else 0
    progress_done = 0

    def _stage(stage):
        if progress_cb and total_steps:
            progress_cb(stage, progress_done, total_steps)

    def _tick(stage):
        nonlocal progress_done
        progress_done += 1
        if progress_cb and total_steps:
            progress_cb(stage, progress_done, total_steps)

    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        if download_config:
            _stage("config_json (start)")
            t0 = datetime.now().timestamp()
            zf.writestr(config_filename, json.dumps(config_payload, indent=2))
            timings["config_json_s"] = datetime.now().timestamp() - t0
            _tick("config_json")
        if download_results:
            _stage("results_csv (start)")
            t0 = datetime.now().timestamp()
            zf.writestr("results.csv", results.to_csv(index=False))
            timings["results_csv_s"] = datetime.now().timestamp() - t0
            _tick("results_csv")
        if download_long_df and analyses:
            _stage("long_df_csv (start)")
            t0 = datetime.now().timestamp()
            zf.writestr("long_df.csv", analyses[0]["long_df"].to_csv(index=False))
            timings["long_df_csv_s"] = datetime.now().timestamp() - t0
            _tick("long_df_csv")
        if download_plots:
            _stage("plots_html (start)")
            t0 = datetime.now().timestamp()
            for idx, (label, fig) in enumerate(plot_artifacts, start=1):
                if selected_set and label not in selected_set:
                    continue
                _stage(f"plot_html:{label}")
                html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
                safe_label = _safe_filename(label)
                zf.writestr(f"plots/plot_{idx}_{safe_label}.html", html)
                _tick(f"plot_html:{label}")
            timings["plots_html_s"] = datetime.now().timestamp() - t0
    bundle.seek(0)
    timings["total_s"] = datetime.now().timestamp() - total_start
    return bundle.getvalue(), zip_filename, warnings, timings
