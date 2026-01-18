import os
import re

import numpy as np
import pandas as pd

from odyssey.io_utils import _parse_time_series


def _long_format_from_map(wide_df, time_col, column_map):
    frames = []
    time_vals = wide_df[time_col]

    for _, row in column_map.iterrows():
        col = row["column"]
        if col not in wide_df.columns:
            continue
        treatment = row.get("treatment", col)
        try:
            replicate = int(row.get("replicate", 1))
        except (TypeError, ValueError):
            replicate = 1
        tmp = pd.DataFrame(
            {
                "time": time_vals,
                "treatment": treatment,
                "replicate": replicate,
                "od": wide_df[col],
            }
        )
        frames.append(tmp)

    if not frames:
        return pd.DataFrame(columns=["time", "treatment", "replicate", "od"])

    return pd.concat(frames, ignore_index=True)


def _linear_fit(x, y):
    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs[0], coeffs[1]
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else np.nan
    return slope, intercept, r2


def _best_window_fit(x, y, min_points=5, min_slope=0.0, anchor_start=False):
    best = {"score": -np.inf}
    n = len(x)
    start_indices = [0] if anchor_start else range(0, n - min_points + 1)
    for i in start_indices:
        for j in range(i + min_points, n + 1):
            xw = x[i:j]
            yw = y[i:j]
            slope, intercept, r2 = _linear_fit(xw, yw)
            if slope <= min_slope:
                continue
            if np.isnan(r2):
                continue
            window_fraction = len(xw) / n
            score = r2 + 0.02 * np.tanh(slope) + 0.01 * window_fraction
            if score > best["score"]:
                best = {
                    "slope": slope,
                    "intercept": intercept,
                    "r2": r2,
                    "score": score,
                    "n": len(xw),
                    "t_min": float(xw[0]),
                    "t_max": float(xw[-1]),
                }
    return best


def _detect_exponential_start(x, y):
    if len(x) < 4:
        return None
    dy = np.diff(y)
    dx = np.diff(x)
    valid = dx > 0
    if not valid.any():
        return None
    slopes = np.zeros_like(dy)
    slopes[valid] = dy[valid] / dx[valid]
    if len(slopes) < 3:
        return None
    kernel = np.ones(3) / 3
    smooth = np.convolve(slopes, kernel, mode="same")
    max_slope = np.nanmax(smooth)
    if not np.isfinite(max_slope) or max_slope <= 0:
        return None
    threshold = 0.35 * max_slope
    for idx, val in enumerate(smooth):
        if val >= threshold:
            return idx
    return None


def fit_growth_rates(
    df,
    time_col="time",
    value_col="od",
    group_cols=("treatment", "replicate"),
    time_window=None,
    auto_window=False,
    min_points=5,
):
    results = []

    for group, g in df.groupby(list(group_cols)):
        g = g.dropna(subset=[time_col, value_col]).copy()
        g = g[g[value_col] > 0]

        if time_window is not None:
            t_min, t_max = time_window
            g = g[(g[time_col] >= t_min) & (g[time_col] <= t_max)]

        if len(g) < 2:
            results.append(
                {
                    "treatment": group[0],
                    "replicate": group[1],
                    "n": len(g),
                    "mu": np.nan,
                    "intercept": np.nan,
                    "r2": np.nan,
                    "doubling_time": np.nan,
                    "window_start": np.nan,
                    "window_end": np.nan,
                }
            )
            continue

        g = g.sort_values(time_col)
        x = g[time_col].to_numpy(dtype=float)
        y = np.log(g[value_col].to_numpy(dtype=float))
        if auto_window and time_window is None:
            best = _best_window_fit(x, y, min_points=min_points, min_slope=0.0)
            if not best:
                slope = intercept = r2 = np.nan
                doubling = np.nan
                n = len(g)
                t_min = np.nan
                t_max = np.nan
            else:
                slope = best["slope"]
                intercept = best["intercept"]
                r2 = best["r2"]
                doubling = np.log(2) / slope if slope != 0 else np.nan
                n = best["n"]
                t_min = best["t_min"]
                t_max = best["t_max"]
        else:
            slope, intercept, r2 = _linear_fit(x, y)
            doubling = np.log(2) / slope if slope != 0 else np.nan
            n = len(g)
            t_min = float(x[0])
            t_max = float(x[-1])

        results.append(
            {
                "treatment": group[0],
                "replicate": group[1],
                "n": n,
                "mu": slope,
                "intercept": intercept,
                "r2": r2,
                "doubling_time": doubling,
                "window_start": t_min,
                "window_end": t_max,
            }
        )

    return pd.DataFrame(results)


def _base_time_unit(time_unit):
    return "minutes" if time_unit == "hh:mm:ss" else time_unit


def _convert_growth_rate(mu_series, base_unit, target_unit):
    if base_unit == target_unit:
        return mu_series
    if base_unit == "minutes" and target_unit == "hours":
        return mu_series * 60.0
    if base_unit == "hours" and target_unit == "minutes":
        return mu_series / 60.0
    return mu_series


def _convert_duration(dt_series, base_unit, target_unit):
    if base_unit == target_unit:
        return dt_series
    if base_unit == "minutes" and target_unit == "hours":
        return dt_series / 60.0
    if base_unit == "hours" and target_unit == "minutes":
        return dt_series * 60.0
    return dt_series


def _convert_auc(auc_series, base_unit, target_unit):
    if base_unit == target_unit:
        return auc_series
    if base_unit == "minutes" and target_unit == "hours":
        return auc_series / 60.0
    if base_unit == "hours" and target_unit == "minutes":
        return auc_series * 60.0
    return auc_series


def _build_column_map(available_cols, replicate_groups):
    if replicate_groups:
        column_map = []
        for group in replicate_groups:
            for idx, col in enumerate(group["columns"], start=1):
                column_map.append(
                    {"column": col, "treatment": group["treatment"], "replicate": idx}
                )
        return column_map
    return [{"column": col, "treatment": str(col), "replicate": 1} for col in available_cols]


def _mean_sd_by_treatment_time(df):
    grouped = df.groupby(["treatment", "time"])["od"]
    return (
        grouped.agg(mean="mean", sd=lambda x: x.std(ddof=1))
        .reset_index()
        .sort_values(["treatment", "time"])
    )


def _strip_replicate_suffix(name):
    return re.sub(r"[._-]\\d+$", "", str(name)).strip()


def _suggest_treatment_name(columns):
    if not columns:
        return ""
    bases = [_strip_replicate_suffix(c) for c in columns]
    unique_bases = {b for b in bases if b}
    if len(unique_bases) == 1:
        return unique_bases.pop()
    prefix = os.path.commonprefix([str(c) for c in columns]).strip()
    if prefix:
        return prefix.rstrip("._- ")
    return str(columns[0])


def _compute_auc(
    df,
    time_col="time",
    value_col="od",
    group_cols=("treatment", "replicate"),
    time_window=None,
):
    rows = []
    for group, g in df.groupby(list(group_cols)):
        g = g.dropna(subset=[time_col, value_col]).sort_values(time_col)
        if time_window is not None:
            t_min, t_max = time_window
            g = g[(g[time_col] >= t_min) & (g[time_col] <= t_max)]
        if len(g) < 2:
            auc = np.nan
        else:
            x = g[time_col].to_numpy(dtype=float)
            y = g[value_col].to_numpy(dtype=float)
            try:
                auc = np.trapezoid(y, x)
            except AttributeError:
                auc = np.trapz(y, x)
        rows.append(
            {
                "treatment": group[0],
                "replicate": group[1],
                "auc": auc,
            }
        )
    return pd.DataFrame(rows)


def _validate_data(df, time_col, data_cols):
    issues = []
    if time_col not in df.columns:
        issues.append("Time column not found.")
        return issues
    time_vals = _parse_time_series(df[time_col])
    if time_vals.isna().all():
        issues.append("Time column could not be parsed.")
    if time_vals.isna().sum() > 0:
        issues.append("Time column has missing/invalid values.")
    for col in data_cols:
        if col not in df.columns:
            issues.append(f"Missing column: {col}")
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        if series.isna().sum() > 0:
            issues.append(f"{col}: missing values detected.")
        if (series <= 0).sum() > 0:
            issues.append(f"{col}: non-positive OD values detected.")
    return issues


def _qc_flags(results_df, r2_threshold=0.9):
    flags = []
    for _, row in results_df.iterrows():
        issues = []
        if pd.notna(row.get("r2")) and row["r2"] < r2_threshold:
            issues.append(f"low_r2(<{r2_threshold})")
        if pd.notna(row.get("mu")) and row["mu"] <= 0:
            issues.append("non_positive_mu")
        flags.append(", ".join(issues) if issues else "")
    out = results_df.copy()
    out["qc_flags"] = flags
    return out


def _window_r2_by_treatment(long_df, time_window=None):
    rows = []
    for treatment, g in long_df.groupby("treatment"):
        g = g.dropna(subset=["time", "od"]).copy()
        g = g[g["od"] > 0]
        if time_window is not None:
            t_min, t_max = time_window
            g = g[(g["time"] >= t_min) & (g["time"] <= t_max)]
        if len(g) < 2:
            rows.append({"treatment": treatment, "r2": np.nan})
            continue
        x = g["time"].to_numpy(dtype=float)
        y = np.log(g["od"].to_numpy(dtype=float))
        _, _, r2 = _linear_fit(x, y)
        rows.append({"treatment": treatment, "r2": r2})
    return pd.DataFrame(rows)


def _auto_window_from_long_df(long_df, min_points=5):
    windows = []
    for _, g in long_df.groupby("treatment"):
        g = g.dropna(subset=["time", "od"]).copy()
        g = g[g["od"] > 0].sort_values("time")
        if len(g) < min_points:
            continue
        x = g["time"].to_numpy(dtype=float)
        y = np.log(g["od"].to_numpy(dtype=float))
        start_idx = _detect_exponential_start(x, y)
        if start_idx is None:
            best = _best_window_fit(x, y, min_points=min_points, anchor_start=True)
        else:
            xw = x[start_idx:]
            yw = y[start_idx:]
            if len(xw) < min_points:
                best = _best_window_fit(x, y, min_points=min_points, anchor_start=True)
            else:
                best = _best_window_fit(xw, yw, min_points=min_points, anchor_start=True)
        if best and not np.isnan(best.get("t_min", np.nan)):
            windows.append((best["t_min"], best["t_max"]))
    if not windows:
        return None
    starts = [w[0] for w in windows]
    ends = [w[1] for w in windows]
    return (float(np.median(starts)), float(np.median(ends)))
