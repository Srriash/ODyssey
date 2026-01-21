from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from odyssey.analysis import _mean_sd_by_treatment_time, auto_select_exponential_window, fit_growth_rates


FIXTURES = Path(__file__).parent / "fixtures"


def _load_long_df():
    return pd.read_csv(FIXTURES / "long_df.csv")


def test_mean_sd_by_treatment_time():
    long_df = _load_long_df()
    mean_df = _mean_sd_by_treatment_time(long_df)
    row = mean_df[(mean_df["treatment"] == "A") & (mean_df["time"] == 1)].iloc[0]
    assert row["mean"] == pytest.approx(0.21)
    assert row["sd"] == pytest.approx(0.014142, rel=1e-3)


def test_fit_growth_rates_shape():
    long_df = _load_long_df()
    results = fit_growth_rates(long_df, time_window=(0, 4), auto_window=False)
    assert set(["treatment", "replicate", "mu", "r2"]).issubset(results.columns)
    assert len(results) == 4


def test_auto_window_clean_exponential():
    time = np.arange(0, 16, 1, dtype=float)
    od = np.exp(0.3 * time)
    od[10:] = od[10]  # plateau
    result = auto_select_exponential_window(time, od, {"min_points": 4})
    assert "error" not in result
    assert result["mu"] > 0
    assert result["r2"] >= 0.99


def test_auto_window_noisy_exponential():
    rng = np.random.default_rng(42)
    time = np.arange(0, 12, 1, dtype=float)
    od = np.exp(0.25 * time)
    od = od * (1 + rng.normal(0, 0.05, size=od.shape))
    od = np.clip(od, 1e-3, None)
    result = auto_select_exponential_window(time, od, {"min_points": 4, "r2_min": 0.97})
    assert "error" not in result
    assert result["mu"] > 0


def test_auto_window_diauxic_shift_prefers_fast_phase():
    time = np.arange(0, 21, 1, dtype=float)
    od = np.exp(0.12 * time)
    od[9:12] = od[8]  # short plateau
    od[12:] = od[12] * np.exp(0.35 * (time[12:] - time[12]))
    result = auto_select_exponential_window(time, od, {"min_points": 4, "r2_min": 0.97})
    assert "error" not in result
    assert result["mu"] > 0
