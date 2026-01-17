from pathlib import Path

import pandas as pd

from odyssey.analysis import _mean_sd_by_treatment_time
from odyssey.plotting import _plot_overlay


FIXTURES = Path(__file__).parent / "fixtures"


def test_plot_overlay_traces():
    long_df = pd.read_csv(FIXTURES / "long_df.csv")
    mean_df = _mean_sd_by_treatment_time(long_df)
    fig = _plot_overlay(mean_df, ["A", "B"], show_sd=True)
    assert len(fig.data) > 0
