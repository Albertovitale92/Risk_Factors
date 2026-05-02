import pandas as pd
import numpy as np
import pytest

from risk_factors.transformations import (
    rolling_correlation,
    rolling_mean,
    rolling_volatility,
)


def test_rolling_mean_and_volatility_for_series():
    values = pd.Series([1.0, 2.0, 3.0, 4.0])

    mean = rolling_mean(values, window=2)
    volatility = rolling_volatility(values, window=2)

    assert mean.tolist() == pytest.approx([np.nan, 1.5, 2.5, 3.5], nan_ok=True)
    assert volatility.iloc[-1] == pytest.approx(2**0.5 / 2)


def test_rolling_correlation_between_series():
    left = pd.Series([1.0, 2.0, 3.0, 4.0])
    right = pd.Series([2.0, 4.0, 6.0, 8.0])

    corr = rolling_correlation(left, right, window=3)

    assert corr.iloc[-1] == pytest.approx(1.0)
