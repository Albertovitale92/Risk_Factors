"""Duration analytics for cashflows and curves."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_cashflow_series(cashflows: pd.Series | list[float] | tuple[float, ...]) -> pd.Series:
    if isinstance(cashflows, pd.Series):
        series = cashflows.copy()
    else:
        series = pd.Series(cashflows)
    return pd.to_numeric(series, errors="coerce").dropna()


def _cashflow_times(cashflows: pd.Series) -> np.ndarray:
    if np.issubdtype(cashflows.index.dtype, np.number):
        return cashflows.index.to_numpy(dtype=float)
    return np.arange(1, len(cashflows) + 1, dtype=float)


def _yield_array(yields, length: int) -> np.ndarray:
    if np.isscalar(yields):
        return np.full(length, float(yields))
    if isinstance(yields, pd.Series):
        values = pd.to_numeric(yields, errors="coerce").to_numpy(dtype=float)
    else:
        values = np.asarray(yields, dtype=float)
    if len(values) != length:
        raise ValueError("yields must be scalar or have one value per cashflow")
    return values


def macaulay_duration(cashflows, yields) -> float:
    """Compute Macaulay duration from cashflows and scalar or per-period yields."""
    cashflow_series = _to_cashflow_series(cashflows)
    if cashflow_series.empty:
        return np.nan

    times = _cashflow_times(cashflow_series)
    yield_values = _yield_array(yields, len(cashflow_series))
    discount_factors = 1 / (1 + yield_values) ** times
    present_values = cashflow_series.to_numpy(dtype=float) * discount_factors
    price = present_values.sum()
    if price == 0 or pd.isna(price):
        return np.nan

    return float((times * present_values).sum() / price)


def modified_duration(cashflows, yields) -> float:
    """Compute modified duration from cashflows and yields."""
    macaulay = macaulay_duration(cashflows, yields)
    if pd.isna(macaulay):
        return np.nan

    if np.isscalar(yields):
        reference_yield = float(yields)
    else:
        reference_yield = float(np.nanmean(_yield_array(yields, len(_to_cashflow_series(cashflows)))))
    return float(macaulay / (1 + reference_yield))


def key_rate_durations(curve: pd.Series, shocks: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Compute key-rate sensitivities as negative curve changes divided by shocks.

    ``curve`` is a Series of base rates by tenor. ``shocks`` can be a Series
    of shocked rates by tenor or a DataFrame of shocked scenarios by tenor.
    """
    if not isinstance(curve, pd.Series):
        raise TypeError("curve must be a pandas Series")
    base_curve = pd.to_numeric(curve, errors="coerce")

    if isinstance(shocks, pd.Series):
        shocked_curve = pd.to_numeric(shocks, errors="coerce")
        aligned = pd.concat([base_curve, shocked_curve], axis=1, join="inner").dropna()
        aligned.columns = ["base", "shocked"]
        rate_change = aligned["shocked"] - aligned["base"]
        return -rate_change.rename("key_rate_duration")

    if isinstance(shocks, pd.DataFrame):
        numeric_shocks = shocks.apply(pd.to_numeric, errors="coerce")
        aligned_base = base_curve.reindex(numeric_shocks.columns)
        return -(numeric_shocks.subtract(aligned_base, axis=1))

    raise TypeError("shocks must be a pandas Series or DataFrame")
