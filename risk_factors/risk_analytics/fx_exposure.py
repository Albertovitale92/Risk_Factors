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


def compute_fx_exposure(
    positions: pd.DataFrame,
    fx_rates: pd.Series,
    base_currency: str,
) -> pd.DataFrame:
    """Compute FX exposure by currency in the selected base currency.

    ``fx_rates`` should contain base-currency value per one unit of each
    exposure currency. The selected base currency is assigned an FX rate of 1
    if it is not explicitly provided.
    """
    if not isinstance(fx_rates, pd.Series):
        raise TypeError("fx_rates must be a pandas Series")

    local_exposure = _positions_by_currency(positions)
    numeric_rates = pd.to_numeric(fx_rates, errors="coerce").copy()
    if base_currency not in numeric_rates.index:
        numeric_rates.loc[base_currency] = 1.0

    aligned = pd.concat([local_exposure, numeric_rates], axis=1, join="inner")
    aligned.columns = ["local_exposure", "fx_rate"]
    aligned["base_exposure"] = aligned["local_exposure"] * aligned["fx_rate"]
    aligned["base_currency"] = base_currency
    aligned.index.name = "currency"
    return aligned


def portfolio_fx_sensitivity(
    positions: pd.DataFrame,
    fx_rates: pd.Series,
    base_currency: str,
    shock_size: float = 0.0001,
) -> pd.DataFrame:
    """Compute standardized FX spot sensitivity by currency.

    The default shock size is 1 bp as a relative spot move.
    """
    exposure = compute_fx_exposure(positions, fx_rates, base_currency)
    exposure["shock_size"] = shock_size
    exposure["fx_sensitivity"] = exposure["base_exposure"] * shock_size
    return exposure[["base_exposure", "base_currency", "shock_size", "fx_sensitivity"]]


def portfolio_fx_scenario_pnl(
    positions: pd.DataFrame,
    fx_rates: pd.Series,
    base_currency: str,
    fx_returns: pd.Series | pd.DataFrame,
) -> pd.Series | pd.DataFrame:
    """Compute FX-driven P&L under realised or scenario FX returns."""
    exposure = compute_fx_exposure(positions, fx_rates, base_currency)
    base_exposure = exposure["base_exposure"]

    if isinstance(fx_returns, pd.DataFrame):
        numeric_returns = fx_returns.apply(pd.to_numeric, errors="coerce")
        return numeric_returns.multiply(base_exposure.reindex(numeric_returns.columns), axis=1)

    if isinstance(fx_returns, pd.Series):
        returns = pd.to_numeric(fx_returns, errors="coerce")
        return (base_exposure.reindex(returns.index) * returns).rename("fx_scenario_pnl")

    raise TypeError("fx_returns must be a pandas Series or DataFrame")
