import pandas as pd
import pytest

from risk_factors.risk_metrics import historical_var, parametric_normaldist_var


def test_historical_var_returns_positive_loss():
    pnl = pd.Series([-100.0, -50.0, 0.0, 25.0, 50.0])

    assert historical_var(pnl, confidence=0.8) == pytest.approx(60.0)


def test_parametric_normaldist_var_returns_positive_loss():
    pnl = pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0])

    assert parametric_normaldist_var(pnl, confidence=0.95) > 0


def test_var_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        historical_var(pd.Series([1.0, 2.0]), confidence=1.0)
