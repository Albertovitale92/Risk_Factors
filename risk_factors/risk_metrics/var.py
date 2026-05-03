"""Value-at-Risk metrics."""

from __future__ import annotations

import pandas as pd

from risk_factors.distributions import fit_normaldist_distribution


def _validate_confidence(confidence: float) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    return confidence


def _to_numeric_series(values: pd.Series, name: str) -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    return pd.to_numeric(values, errors="coerce").dropna()


def historical_var(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Compute historical VaR from a P&L series as a positive loss.

    Input convention: losses are negative P&L values.
    Output convention: VaR is returned as a positive loss number.
    """
    confidence = _validate_confidence(confidence)
    pnl_series = _to_numeric_series(pnl, "pnl")
    if pnl_series.empty:
        return float("nan")

    tail_quantile = pnl_series.quantile(1 - confidence)
    return float(max(-tail_quantile, 0.0))


def parametric_normaldist_var(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Compute normal parametric VaR from a P&L series as a positive loss."""
    confidence = _validate_confidence(confidence)
    fitted_distribution = fit_normaldist_distribution(pnl, name="pnl")
    if fitted_distribution.sample_size == 0 or pd.isna(fitted_distribution.volatility):
        return float("nan")

    tail_pnl = fitted_distribution.quantile(1 - confidence)
    return float(max(-tail_pnl, 0.0))
