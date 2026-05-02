import pandas as pd
import pytest

from risk_factors.risk_metrics import compute_beta, compute_multi_beta


def test_compute_beta_against_benchmark():
    benchmark = pd.Series([0.01, 0.02, 0.03, 0.04])
    asset = benchmark * 2

    assert compute_beta(asset, benchmark) == pytest.approx(2.0)


def test_compute_multi_beta_for_dataframe():
    benchmark = pd.Series([0.01, 0.02, 0.03, 0.04])
    returns = pd.DataFrame({"asset_a": benchmark, "asset_b": benchmark * -1})

    betas = compute_multi_beta(returns, benchmark)

    assert betas["asset_a"] == pytest.approx(1.0)
    assert betas["asset_b"] == pytest.approx(-1.0)
