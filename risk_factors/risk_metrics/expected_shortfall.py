"""Expected shortfall metrics."""

from __future__ import annotations

from math import exp, pi

import pandas as pd

from risk_factors.distributions import fit_normaldist_distribution
from risk_factors.risk_metrics.var import _to_numeric_series, _validate_confidence


def historical_expected_shortfall(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Compute historical expected shortfall as a positive loss.

    Input convention: losses are negative P&L values.
    Output convention: expected shortfall is returned as a positive loss number.
    """
    confidence = _validate_confidence(confidence)
    pnl_series = _to_numeric_series(pnl, "pnl")
    if pnl_series.empty:
        return float("nan")

    tail_quantile = pnl_series.quantile(1 - confidence)
    tail_losses = pnl_series[pnl_series <= tail_quantile]
    if tail_losses.empty:
        return float("nan")
    return float(max(-tail_losses.mean(), 0.0))


def parametric_expected_shortfall(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Compute normal parametric expected shortfall as a positive loss."""
    confidence = _validate_confidence(confidence)
    fitted_distribution = fit_normaldist_distribution(pnl, name="pnl")
    if fitted_distribution.sample_size == 0 or pd.isna(fitted_distribution.volatility):
        return float("nan")
    if fitted_distribution.volatility == 0:
        return float(max(-fitted_distribution.mean, 0.0))

    tail_z_score = fitted_distribution.quantile(1 - confidence)
    standard_normal_z_score = (tail_z_score - fitted_distribution.mean) / fitted_distribution.volatility
    standard_normal_pdf = exp(-(standard_normal_z_score**2) / 2) / (2 * pi) ** 0.5
    tail_pnl = fitted_distribution.mean - (
        fitted_distribution.volatility * standard_normal_pdf / (1 - confidence)
    )
    return float(max(-tail_pnl, 0.0))
