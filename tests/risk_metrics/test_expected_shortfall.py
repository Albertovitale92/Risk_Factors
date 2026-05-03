import pandas as pd

from risk_factors.risk_metrics import (
    historical_expected_shortfall,
    parametric_expected_shortfall,
)


def test_historical_expected_shortfall_returns_tail_average_loss():
    pnl = pd.Series([-100.0, -50.0, 0.0, 25.0, 50.0])

    assert historical_expected_shortfall(pnl, confidence=0.8) == 100.0


def test_parametric_expected_shortfall_returns_positive_loss():
    pnl = pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0])

    assert parametric_expected_shortfall(pnl, confidence=0.95) > 0
