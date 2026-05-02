"""Risk metric calculations and aggregation utilities."""

from risk_factors.risk_metrics.beta import compute_beta, compute_multi_beta
from risk_factors.risk_metrics.duration import (
    key_rate_durations,
    macaulay_duration,
    modified_duration,
)
from risk_factors.risk_metrics.factor_model import (
    factor_risk_contribution,
    ols_factor_exposures,
    pca_factors,
)
from risk_factors.risk_metrics.fx_exposure import (
    compute_fx_exposure,
    portfolio_fx_sensitivity,
)

__all__ = [
    "compute_beta",
    "compute_fx_exposure",
    "compute_multi_beta",
    "factor_risk_contribution",
    "key_rate_durations",
    "macaulay_duration",
    "modified_duration",
    "ols_factor_exposures",
    "pca_factors",
    "portfolio_fx_sensitivity",
]
