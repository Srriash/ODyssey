from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from odyssey.analysis import _compute_auc, _mean_sd_by_treatment_time, _qc_flags, fit_growth_rates


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
    assert set(["treatment", "replicate", "mu", "r2", "window_start", "window_end"]).issubset(
        results.columns
    )
    assert len(results) == 4


def test_compute_auc():
    long_df = _load_long_df()
    auc_df = _compute_auc(long_df, time_window=(0, 4))
    row = auc_df[(auc_df["treatment"] == "A") & (auc_df["replicate"] == 1)].iloc[0]
    assert row["auc"] == pytest.approx(1.95)


def test_qc_flags():
    df = pd.DataFrame(
        {
            "mu": [0.2, -0.1, 0.3],
            "r2": [0.95, 0.99, 0.5],
        }
    )
    flagged = _qc_flags(df, r2_threshold=0.9)
    assert flagged["qc_flags"].tolist() == ["", "non_positive_mu", "low_r2(<0.9)"]
