import pandas as pd
import pytest

from risk_factors.risk_metrics import compute_fx_exposure, portfolio_fx_sensitivity


def test_compute_fx_exposure_groups_positions_by_currency():
    positions = pd.DataFrame(
        {
            "currency": ["EUR", "USD", "EUR"],
            "amount": [100.0, 50.0, 25.0],
        }
    )
    fx_rates = pd.Series({"EUR": 1.1, "USD": 1.0})

    exposure = compute_fx_exposure(positions, fx_rates)

    assert exposure.loc["EUR", "local_exposure"] == pytest.approx(125.0)
    assert exposure.loc["EUR", "base_exposure"] == pytest.approx(137.5)
    assert exposure.loc["USD", "base_exposure"] == pytest.approx(50.0)


def test_portfolio_fx_sensitivity_for_series_and_dataframe_returns():
    positions = pd.DataFrame({"currency": ["EUR", "USD"], "amount": [100.0, 50.0]})
    fx_return = pd.Series({"EUR": 0.01, "USD": -0.02})
    fx_returns = pd.DataFrame(
        [{"EUR": 0.01, "USD": -0.02}, {"EUR": -0.01, "USD": 0.02}]
    )

    sensitivity = portfolio_fx_sensitivity(positions, fx_return)
    scenario_sensitivity = portfolio_fx_sensitivity(positions, fx_returns)

    assert sensitivity["EUR"] == pytest.approx(1.0)
    assert sensitivity["USD"] == pytest.approx(-1.0)
    assert scenario_sensitivity.loc[1, "EUR"] == pytest.approx(-1.0)
    assert scenario_sensitivity.loc[1, "USD"] == pytest.approx(1.0)
