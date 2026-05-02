import numpy as np
import pandas as pd
import pytest

from risk_factors.transformations import (
    abs_return,
    cumulative_return,
    log_return,
    rel_returns,
)


def test_rel_returns_overlapping_and_non_overlapping():
    prices = pd.Series([100.0, 110.0, 121.0, 133.1])

    overlapping = rel_returns(prices, days=2, overlapping=True)
    non_overlapping = rel_returns(prices, days=2, overlapping=False)

    assert overlapping.tolist() == pytest.approx([np.nan, np.nan, 0.21, 0.21], nan_ok=True)
    assert non_overlapping.tolist() == pytest.approx([np.nan, np.nan, 0.21, np.nan], nan_ok=True)


def test_abs_and_log_returns():
    prices = pd.Series([100.0, 110.0, 121.0])

    assert abs_return(prices).tolist() == pytest.approx([np.nan, 10.0, 11.0], nan_ok=True)
    assert log_return(prices).tolist() == pytest.approx(
        [np.nan, np.log(1.1), np.log(1.1)],
        nan_ok=True,
    )


def test_cumulative_return_by_return_type_and_observation_bounds():
    prices = pd.Series(
        [100.0, 105.0, 110.0, 120.0],
        index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]),
    )

    rel = cumulative_return(
        prices,
        start_obs=pd.Timestamp("2025-01-02"),
        end_obs=pd.Timestamp("2025-01-04"),
        return_type="rel",
    )
    absolute = cumulative_return(prices, start_obs=1, end_obs=3, return_type="abs")
    log = cumulative_return(prices, start_obs=1, end_obs=3, return_type="log")

    assert rel.tolist() == pytest.approx([0.0, 110.0 / 105.0 - 1.0, 120.0 / 105.0 - 1.0])
    assert absolute.tolist() == pytest.approx([0.0, 5.0, 15.0])
    assert log.tolist() == pytest.approx([0.0, np.log(110.0 / 105.0), np.log(120.0 / 105.0)])


def test_cumulative_return_rejects_invalid_return_type():
    with pytest.raises(ValueError):
        cumulative_return(pd.Series([1.0, 2.0]), return_type="simple")
