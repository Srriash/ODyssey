import io

import pandas as pd
import streamlit as st

from odyssey.analysis import _compute_auc, _long_format_from_map, _mean_sd_by_treatment_time, fit_growth_rates
from odyssey.io_utils import _apply_time_unit, _parse_time_series, _read_excel_file


@st.cache_data(show_spinner=False)
def _cached_preview_data(
    file_bytes,
    sheet_name,
    time_col,
    time_unit,
    column_map_json,
    blank_normalized,
    blank_col,
):
    uploaded = io.BytesIO(file_bytes)
    df = _read_excel_file(uploaded, sheet_name)
    if not blank_normalized and blank_col:
        data_cols = [c for c in df.columns if c != time_col]
        numeric = df[data_cols].apply(pd.to_numeric, errors="coerce")
        if isinstance(blank_col, (list, tuple, pd.Index)):
            blank_cols = list(blank_col)
        else:
            blank_cols = [blank_col]
        blank_values = df[blank_cols].apply(pd.to_numeric, errors="coerce")
        blank_mean = blank_values.mean(axis=1)
        df[data_cols] = numeric.sub(blank_mean, axis=0)
    time_series = _parse_time_series(df[time_col])
    time_series = _apply_time_unit(time_series, time_unit if time_unit != "hh:mm:ss" else "minutes")
    working_df = df.copy()
    working_df["_time_numeric"] = time_series
    column_map = pd.read_json(io.StringIO(column_map_json))
    long_df = _long_format_from_map(working_df, "_time_numeric", column_map)
    mean_df = _mean_sd_by_treatment_time(long_df)
    time_vals = time_series.dropna()
    t_min = float(time_vals.min()) if not time_vals.empty else 0.0
    t_max = float(time_vals.max()) if not time_vals.empty else 1.0
    return mean_df, long_df, t_min, t_max


@st.cache_data(show_spinner=False)
def _cached_analysis_data(
    file_bytes,
    sheet_name,
    time_col,
    time_unit,
    column_map_json,
    time_window,
    min_points,
    blank_normalized,
    blank_cols,
    auc_window,
):
    uploaded = io.BytesIO(file_bytes)
    df = _read_excel_file(uploaded, sheet_name)
    if not blank_normalized and blank_cols:
        data_cols = [c for c in df.columns if c != time_col]
        numeric = df[data_cols].apply(pd.to_numeric, errors="coerce")
        if isinstance(blank_cols, (list, tuple, pd.Index)):
            blank_list = list(blank_cols)
        else:
            blank_list = [blank_cols]
        blank_values = df[blank_list].apply(pd.to_numeric, errors="coerce")
        blank_mean = blank_values.mean(axis=1)
        df[data_cols] = numeric.sub(blank_mean, axis=0)
    time_series = _parse_time_series(df[time_col])
    time_series = _apply_time_unit(time_series, time_unit if time_unit != "hh:mm:ss" else "minutes")
    working_df = df.copy()
    working_df["_time_numeric"] = time_series
    column_map = pd.read_json(io.StringIO(column_map_json))
    long_df = _long_format_from_map(working_df, "_time_numeric", column_map)
    if long_df.empty:
        raise ValueError("No treatment columns selected.")
    results = fit_growth_rates(
        long_df,
        time_col="time",
        value_col="od",
        group_cols=("treatment", "replicate"),
        time_window=time_window,
        auto_window=False,
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
    return mean_df, long_df, results, auc_df
