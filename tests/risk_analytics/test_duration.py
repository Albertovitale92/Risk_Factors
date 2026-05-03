import pandas as pd
import pytest

from risk_factors.risk_analytics import (
    key_rate_durations,
    macaulay_duration,
    modified_duration,
)


def test_macaulay_and_modified_duration_for_zero_coupon_cashflow():
    cashflows = pd.Series([0.0, 0.0, 100.0], index=[1, 2, 3])

    assert macaulay_duration(cashflows, 0.05) == pytest.approx(3.0)
    assert modified_duration(cashflows, 0.05) == pytest.approx(3.0 / 1.05)


def test_key_rate_durations_for_series_and_dataframe_shocks():
    curve = pd.Series({"1Y": 0.03, "2Y": 0.04})
    shocked_curve = pd.Series({"1Y": 0.031, "2Y": 0.039})
    shock_scenarios = pd.DataFrame(
        [{"1Y": 0.031, "2Y": 0.039}, {"1Y": 0.032, "2Y": 0.041}],
        index=["scenario_1", "scenario_2"],
    )

    series_result = key_rate_durations(curve, shocked_curve)
    frame_result = key_rate_durations(curve, shock_scenarios)

    assert series_result["1Y"] == pytest.approx(-0.001)
    assert series_result["2Y"] == pytest.approx(0.001)
    assert frame_result.loc["scenario_1", "1Y"] == pytest.approx(-0.001)
    assert frame_result.loc["scenario_2", "2Y"] == pytest.approx(-0.001)
