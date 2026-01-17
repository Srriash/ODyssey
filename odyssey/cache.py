import io

import pandas as pd
import streamlit as st

from odyssey.analysis import _long_format_from_map, _mean_sd_by_treatment_time
from odyssey.io_utils import _apply_time_unit, _parse_time_series, _read_excel_file


@st.cache_data(show_spinner=False)
def _cached_preview_data(file_bytes, sheet_name, time_col, time_unit, column_map_json):
    uploaded = io.BytesIO(file_bytes)
    df = _read_excel_file(uploaded, sheet_name)
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
