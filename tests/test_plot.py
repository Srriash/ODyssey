from pathlib import Path

import pandas as pd

from odyssey.analysis import _mean_sd_by_treatment_time
from odyssey.plotting import _plot_compare_runs, _plot_overlay, _plot_small_multiples


FIXTURES = Path(__file__).parent / "fixtures"


def test_plot_overlay_traces():
    long_df = pd.read_csv(FIXTURES / "long_df.csv")
    mean_df = _mean_sd_by_treatment_time(long_df)
    fig = _plot_overlay(mean_df, ["A", "B"], show_sd=True)
    assert len(fig.data) > 0


def test_plot_small_multiples_traces():
    long_df = pd.read_csv(FIXTURES / "long_df.csv")
    mean_df = _mean_sd_by_treatment_time(long_df)
    fig = _plot_small_multiples(mean_df, ["A", "B"], cols_per_row=2, show_sd=True)
    assert len(fig.data) > 0


def test_plot_compare_runs_traces():
    long_df = pd.read_csv(FIXTURES / "long_df.csv")
    mean_df = _mean_sd_by_treatment_time(long_df)
    analyses = [
        {"name": "run_1", "mean_df": mean_df},
        {"name": "run_2", "mean_df": mean_df.copy()},
    ]
    fig = _plot_compare_runs(analyses, "A", show_sd=True)
    assert len(fig.data) > 0
