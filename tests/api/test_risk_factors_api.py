import pandas as pd
import pytest

from risk_factors.api import risk_factors_api as rf


def test_get_returns_accepts_only_canonical_methods():
    prices = pd.Series([100.0, 110.0, 121.0])

    assert rf.get_returns(prices, method="rel").iloc[-1] == pytest.approx(0.1)
    assert rf.get_returns(prices, method="abs").iloc[-1] == pytest.approx(11.0)
    assert rf.get_returns(prices, method="log").iloc[-1] == pytest.approx(0.0953101798)

    with pytest.raises(ValueError):
        rf.get_returns(prices, method="simple")


def test_get_rolling_vol_and_correlation_matrix():
    returns = pd.DataFrame(
        {
            "asset_a": [0.01, 0.02, 0.03, 0.04],
            "asset_b": [0.02, 0.04, 0.06, 0.08],
        }
    )

    vol = rf.get_rolling_vol(returns, window=2)
    corr = rf.get_correlation_matrix(returns)

    assert vol.shape == returns.shape
    assert corr.loc["asset_a", "asset_b"] == pytest.approx(1.0)
