import pandas as pd
import pytest

from risk_factors.transformations import (
    kendall_correlation,
    pairwise_correlation,
    partial_correlation,
    pearson_correlation,
    spearman_correlation,
    tail_correlation,
)


def test_named_correlation_matrices():
    returns = pd.DataFrame(
        {
            "asset_a": [0.01, 0.02, 0.03, 0.04],
            "asset_b": [0.02, 0.04, 0.06, 0.08],
            "asset_c": [0.04, 0.03, 0.02, 0.01],
        }
    )

    assert pearson_correlation(returns).loc["asset_a", "asset_b"] == pytest.approx(1.0)
    assert spearman_correlation(returns).loc["asset_a", "asset_c"] == pytest.approx(-1.0)
    assert kendall_correlation(returns).loc["asset_a", "asset_c"] == pytest.approx(-1.0)


def test_pairwise_correlation_returns_one_row_dataframe():
    x = pd.Series([1.0, 2.0, 3.0], name="x")
    y = pd.Series([2.0, 4.0, 6.0], name="y")

    result = pairwise_correlation(x, y)

    assert list(result.columns) == ["x", "y", "method", "correlation", "n_obs"]
    assert result.loc[0, "correlation"] == pytest.approx(1.0)
    assert result.loc[0, "n_obs"] == 3


def test_tail_and_partial_correlation_shapes():
    returns = pd.DataFrame(
        {
            "asset_a": [-0.10, -0.08, 0.01, 0.02, 0.03],
            "asset_b": [-0.09, -0.07, 0.01, 0.02, 0.04],
            "asset_c": [0.05, 0.04, 0.03, 0.02, 0.01],
        }
    )

    assert tail_correlation(returns, quantile=0.8).shape == (3, 3)
    assert partial_correlation(returns).shape == (3, 3)
