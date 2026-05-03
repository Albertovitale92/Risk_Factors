import pandas as pd
import pytest

from risk_factors.risk_analytics import (
    compute_fx_exposure,
    portfolio_fx_scenario_pnl,
    portfolio_fx_sensitivity,
)


def test_compute_fx_exposure_groups_positions_by_currency():
    positions = pd.DataFrame(
        {
            "currency": ["EUR", "USD", "EUR"],
            "amount": [100.0, 50.0, 25.0],
        }
    )
    fx_rates = pd.Series({"EUR": 1.1, "USD": 1.0})

    exposure = compute_fx_exposure(positions, fx_rates, base_currency="USD")

    assert exposure.loc["EUR", "local_exposure"] == pytest.approx(125.0)
    assert exposure.loc["EUR", "base_exposure"] == pytest.approx(137.5)
    assert exposure.loc["USD", "base_exposure"] == pytest.approx(50.0)
    assert exposure.loc["EUR", "base_currency"] == "USD"


def test_compute_fx_exposure_uses_selected_base_currency():
    positions = pd.DataFrame(
        {
            "currency": ["EUR", "USD"],
            "amount": [100.0, 110.0],
        }
    )
    fx_rates = pd.Series({"USD": 1 / 1.1})

    exposure = compute_fx_exposure(positions, fx_rates, base_currency="EUR")

    assert exposure.loc["EUR", "base_exposure"] == pytest.approx(100.0)
    assert exposure.loc["USD", "base_exposure"] == pytest.approx(100.0)
    assert exposure.loc["USD", "base_currency"] == "EUR"


def test_portfolio_fx_sensitivity_is_standardized_to_shock_size():
    positions = pd.DataFrame({"currency": ["EUR", "USD"], "amount": [100.0, 50.0]})
    fx_rates = pd.Series({"EUR": 1.1, "USD": 1.0})

    sensitivity = portfolio_fx_sensitivity(
        positions,
        fx_rates,
        base_currency="USD",
        shock_size=0.0001,
    )

    assert sensitivity.loc["EUR", "base_exposure"] == pytest.approx(110.0)
    assert sensitivity.loc["EUR", "fx_sensitivity"] == pytest.approx(0.011)
    assert sensitivity.loc["USD", "fx_sensitivity"] == pytest.approx(0.005)


def test_portfolio_fx_scenario_pnl_for_series_and_dataframe_returns():
    positions = pd.DataFrame({"currency": ["EUR", "USD"], "amount": [100.0, 50.0]})
    fx_rates = pd.Series({"EUR": 1.1, "USD": 1.0})
    fx_return = pd.Series({"EUR": 0.01, "USD": -0.02})
    fx_returns = pd.DataFrame(
        [{"EUR": 0.01, "USD": -0.02}, {"EUR": -0.01, "USD": 0.02}]
    )

    scenario_pnl = portfolio_fx_scenario_pnl(
        positions,
        fx_rates,
        base_currency="USD",
        fx_returns=fx_return,
    )
    scenario_pnl_frame = portfolio_fx_scenario_pnl(
        positions,
        fx_rates,
        base_currency="USD",
        fx_returns=fx_returns,
    )

    assert scenario_pnl["EUR"] == pytest.approx(1.1)
    assert scenario_pnl["USD"] == pytest.approx(-1.0)
    assert scenario_pnl_frame.loc[1, "EUR"] == pytest.approx(-1.1)
    assert scenario_pnl_frame.loc[1, "USD"] == pytest.approx(1.0)
