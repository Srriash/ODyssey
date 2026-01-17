import io
import json
import os
import re
import zipfile

import pandas as pd


def _safe_read_json(uploaded):
    try:
        return json.loads(uploaded.getvalue().decode("utf-8"))
    except Exception:
        return None


def _guess_time_columns(df):
    candidates = []
    for col in df.columns:
        name = str(col).lower()
        if "time" in name or "min" in name or "hour" in name:
            candidates.append(col)
    if df.columns.size > 0 and df.columns[0] not in candidates:
        candidates.insert(0, df.columns[0])
    return candidates


def _parse_time_series(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        base = series.iloc[0]
        delta = series - base
        return delta.dt.total_seconds() / 60.0

    if pd.api.types.is_timedelta64_dtype(series):
        return series.dt.total_seconds() / 60.0

    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    str_series = series.astype(str)
    try:
        td = pd.to_timedelta(str_series, errors="raise")
        return td.dt.total_seconds() / 60.0
    except Exception:
        pass

    try:
        dt = pd.to_datetime(str_series, errors="raise")
        base = dt.iloc[0]
        delta = dt - base
        return delta.dt.total_seconds() / 60.0
    except Exception:
        return pd.to_numeric(series, errors="coerce")


def _apply_time_unit(minutes_series, unit_choice):
    if unit_choice == "minutes":
        return minutes_series
    if unit_choice == "hours":
        return minutes_series / 60.0
    return minutes_series


def _read_excel_file(uploaded, sheet_name):
    try:
        xls = pd.ExcelFile(uploaded)
    except Exception as exc:
        raise ValueError(f"Could not read Excel file: {exc}")
    if sheet_name not in xls.sheet_names:
        raise ValueError(f"Sheet '{sheet_name}' not found in {uploaded.name}.")
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, mangle_dupe_cols=False)
    except TypeError:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    return df


def _safe_filename(value):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value))
    return cleaned.strip("_") or "plot"


def _read_results_zip(uploaded_zip):
    try:
        bundle = zipfile.ZipFile(uploaded_zip)
    except zipfile.BadZipFile as exc:
        return None, f"{uploaded_zip.name}: invalid zip ({exc})"
    results_name = None
    config_name = None
    long_df_name = None
    for name in bundle.namelist():
        base = os.path.basename(name)
        if base == "results.csv":
            results_name = name
        elif base == "long_df.csv":
            long_df_name = name
        elif base.endswith(".json") and "config" in base.lower():
            config_name = name
    if results_name is None:
        return None, f"{uploaded_zip.name}: results.csv not found"
    try:
        results_df = pd.read_csv(bundle.open(results_name))
    except Exception as exc:
        return None, f"{uploaded_zip.name}: could not read results.csv ({exc})"
    config = None
    if config_name is not None:
        try:
            config_raw = bundle.open(config_name).read()
            config = json.loads(config_raw.decode("utf-8"))
        except Exception:
            config = None
    long_df = None
    if long_df_name is not None:
        try:
            long_df = pd.read_csv(bundle.open(long_df_name))
        except Exception:
            long_df = None
    return {
        "name": os.path.basename(uploaded_zip.name),
        "results": results_df,
        "config": config,
        "long_df": long_df,
    }, None
