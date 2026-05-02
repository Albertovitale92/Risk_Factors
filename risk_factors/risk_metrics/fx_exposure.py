"""FX exposure analytics."""

from __future__ import annotations

import pandas as pd


def _positions_by_currency(positions: pd.DataFrame) -> pd.Series:
    if not isinstance(positions, pd.DataFrame):
        raise TypeError("positions must be a pandas DataFrame")
    required_columns = {"currency", "amount"}
    missing = required_columns - set(positions.columns)
    if missing:
        raise ValueError(f"positions is missing required columns: {sorted(missing)}")

    amounts = pd.to_numeric(positions["amount"], errors="coerce")
    return amounts.groupby(positions["currency"]).sum()


def compute_fx_exposure(positions: pd.DataFrame, fx_rates: pd.Series) -> pd.DataFrame:
    """Compute FX exposure by currency in local and base-currency terms."""
    if not isinstance(fx_rates, pd.Series):
        raise TypeError("fx_rates must be a pandas Series")

    local_exposure = _positions_by_currency(positions)
    numeric_rates = pd.to_numeric(fx_rates, errors="coerce")
    aligned = pd.concat([local_exposure, numeric_rates], axis=1, join="inner")
    aligned.columns = ["local_exposure", "fx_rate"]
    aligned["base_exposure"] = aligned["local_exposure"] * aligned["fx_rate"]
    aligned.index.name = "currency"
    return aligned


def portfolio_fx_sensitivity(
    positions: pd.DataFrame,
    fx_returns: pd.Series | pd.DataFrame,
) -> pd.Series | pd.DataFrame:
    """Compute portfolio P&L sensitivity to FX returns by currency."""
    local_exposure = _positions_by_currency(positions)

    if isinstance(fx_returns, pd.Series):
        returns = pd.to_numeric(fx_returns, errors="coerce")
        return (local_exposure.reindex(returns.index) * returns).rename("fx_sensitivity")

    if isinstance(fx_returns, pd.DataFrame):
        numeric_returns = fx_returns.apply(pd.to_numeric, errors="coerce")
        return numeric_returns.multiply(local_exposure.reindex(numeric_returns.columns), axis=1)

    raise TypeError("fx_returns must be a pandas Series or DataFrame")
