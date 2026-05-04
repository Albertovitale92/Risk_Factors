"""Public API facade for library consumers."""

from risk_factors.api import risk_factors_api
from risk_factors.api.risk_factors_api import (
    get_commodities_data,
    get_correlation_matrix,
    get_credit_spreads,
    get_ecb_ois_zero_curve,
    get_equity_data,
    get_fx_data,
    get_rates_curve,
    get_returns,
    get_risk_drivers_snapshot,
    get_rolling_vol,
)

__all__ = [
    "get_commodities_data",
    "get_correlation_matrix",
    "get_credit_spreads",
    "get_ecb_ois_zero_curve",
    "get_equity_data",
    "get_fx_data",
    "get_rates_curve",
    "get_returns",
    "get_risk_drivers_snapshot",
    "get_rolling_vol",
    "risk_factors_api",
]
