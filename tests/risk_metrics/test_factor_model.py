import pandas as pd
import pytest

from risk_factors.risk_metrics import (
    factor_risk_contribution,
    ols_factor_exposures,
    pca_factors,
)


def test_ols_factor_exposures_recovers_linear_coefficients():
    factors = pd.DataFrame(
        {
            "factor_a": [1.0, 2.0, 3.0, 4.0],
            "factor_b": [2.0, 0.0, 1.0, 3.0],
        }
    )
    returns = pd.Series(
        0.5 + 2.0 * factors["factor_a"] - 1.0 * factors["factor_b"],
        name="asset",
    )

    exposures = ols_factor_exposures(returns, factors)

    assert exposures.loc["intercept", "asset"] == pytest.approx(0.5)
    assert exposures.loc["factor_a", "asset"] == pytest.approx(2.0)
    assert exposures.loc["factor_b", "asset"] == pytest.approx(-1.0)


def test_pca_factors_returns_scores_variance_and_loadings():
    returns = pd.DataFrame(
        {
            "asset_a": [0.01, 0.02, 0.03, 0.04],
            "asset_b": [0.02, 0.04, 0.06, 0.08],
        }
    )

    scores, explained_variance, loadings = pca_factors(returns)

    assert scores.shape == (4, 2)
    assert explained_variance.sum() == pytest.approx(1.0)
    assert loadings.shape == (2, 2)


def test_factor_risk_contribution_normalizes_variance_contributions():
    exposures = pd.Series({"factor_a": 1.0, "factor_b": 2.0})
    cov_matrix = pd.DataFrame(
        [[0.04, 0.0], [0.0, 0.01]],
        index=["factor_a", "factor_b"],
        columns=["factor_a", "factor_b"],
    )

    contribution = factor_risk_contribution(pd.Series(dtype=float), exposures, cov_matrix)

    assert contribution.sum() == pytest.approx(1.0)
    assert contribution["factor_a"] == pytest.approx(0.5)
    assert contribution["factor_b"] == pytest.approx(0.5)
