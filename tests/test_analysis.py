from pathlib import Path

import pandas as pd
import pytest

from odyssey.analysis import _mean_sd_by_treatment_time, fit_growth_rates


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
