from pathlib import Path

from odyssey.io_utils import _read_results_zip


FIXTURES = Path(__file__).parent / "fixtures"


def test_read_results_zip():
    zip_path = FIXTURES / "odyssey_sample.zip"
    with open(zip_path, "rb") as handle:
        parsed, err = _read_results_zip(handle)
    assert err is None
    assert parsed["results"] is not None
    assert parsed["long_df"] is not None
    assert "treatment" in parsed["results"].columns
