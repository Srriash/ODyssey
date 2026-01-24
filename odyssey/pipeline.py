import pandas as pd

from odyssey.analysis import _compute_auc, _long_format_from_map, _mean_sd_by_treatment_time, fit_growth_rates
from odyssey.io_utils import _apply_time_unit, _parse_time_series, _read_excel_file


def apply_blank_normalization(df, time_col, blank_col):
    working_df = df.copy()
    data_cols = [c for c in working_df.columns if c != time_col]
    numeric = working_df[data_cols].apply(pd.to_numeric, errors="coerce")
    if isinstance(blank_col, (list, tuple, pd.Index)):
        blank_cols = list(blank_col)
    else:
        blank_cols = [blank_col]
    blank_vals = working_df[blank_cols].apply(pd.to_numeric, errors="coerce")
    blank_mean = blank_vals.mean(axis=1)
    working_df[data_cols] = numeric.sub(blank_mean, axis=0)
    return working_df


def analyze_file(
    uploaded,
    sheet_name,
    time_col,
    time_unit,
    column_map,
    time_window,
    auto_window,
    min_points,
    blank_normalized,
    blank_cols,
    auc_window=None,
):
    df = _read_excel_file(uploaded, sheet_name)
    if not blank_normalized and blank_cols:
        df = apply_blank_normalization(df, time_col, blank_cols)
    time_series = _parse_time_series(df[time_col])
    time_series = _apply_time_unit(time_series, time_unit if time_unit != "hh:mm:ss" else "minutes")
    working_df = df.copy()
    working_df["_time_numeric"] = time_series
    if time_series.isna().all():
        raise ValueError(f"Time column could not be parsed in {uploaded.name}.")
    column_map_df = pd.DataFrame(column_map)
    long_df = _long_format_from_map(working_df, "_time_numeric", column_map_df)
    if long_df.empty:
        raise ValueError(f"No treatment columns selected in {uploaded.name}.")
    results = fit_growth_rates(
        long_df,
        time_col="time",
        value_col="od",
        group_cols=("treatment", "replicate"),
        time_window=time_window,
        auto_window=auto_window,
        min_points=min_points,
    )
    mean_df = _mean_sd_by_treatment_time(long_df)
    auc_df = _compute_auc(
        long_df,
        time_col="time",
        value_col="od",
        group_cols=("treatment", "replicate"),
        time_window=auc_window,
    )
    return {
        "name": uploaded.name,
        "long_df": long_df,
        "results": results,
        "mean_df": mean_df,
        "auc": auc_df,
    }
