"""Return transformations for price series."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Literal

import numpy as np
import pandas as pd


ReturnType = Literal["abs", "rel", "log"]


def _resolve_days(days: int | None, periods: int | None) -> int:
    if days is not None and periods is not None:
        raise ValueError("use either days or periods, not both")

    window = periods if periods is not None else days
    if not isinstance(window, int):
        raise TypeError("days must be an integer")
    if window < 1:
        raise ValueError("days must be greater than or equal to 1")
    return window


def _as_numeric_series(values: pd.Series) -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError("values must be a pandas Series")
    return pd.to_numeric(values, errors="coerce")


def _validate_return_type(return_type: ReturnType) -> ReturnType:
    valid_return_types = {"abs", "rel", "log"}
    if return_type not in valid_return_types:
        raise ValueError("return_type must be one of 'abs', 'rel', or 'log'")
    return return_type


def _apply_overlap_filter(returns: pd.Series, periods: int, overlapping: bool) -> pd.Series:
    if overlapping:
        return returns

    filtered = returns.copy()
    valid_positions = np.arange(len(filtered)) >= periods
    valid_positions &= (np.arange(len(filtered)) - periods) % periods == 0
    filtered.iloc[~valid_positions] = np.nan
    return filtered


def _get_observation_position(values: pd.Series, obs: Hashable | None, default: int) -> int:
    if obs is None:
        return default
    if isinstance(obs, int):
        return obs

    positions = values.index.get_indexer([obs])
    if positions[0] == -1:
        raise KeyError(f"observation {obs!r} was not found in the Series index")
    return int(positions[0])


def rel_returns(
    prices: pd.Series,
    days: int = 1,
    overlapping: bool = True,
    *,
    periods: int | None = None,
) -> pd.Series:
    """Compute relative returns over a configurable number of observations.

    Parameters
    ----------
    prices:
        Price series.
    days:
        Number of observations in each return window.
    overlapping:
        If True, compute rolling overlapping returns. If False, keep only
        non-overlapping return windows and set skipped rows to NaN.
    periods:
        Alias for days.
    """
    days = _resolve_days(days, periods)
    numeric_prices = _as_numeric_series(prices)

    returns = numeric_prices.pct_change(periods=days, fill_method=None)
    returns = returns.replace([np.inf, -np.inf], np.nan)
    return _apply_overlap_filter(returns, days, overlapping)


def abs_returns(
    prices: pd.Series,
    days: int = 1,
    overlapping: bool = True,
    *,
    periods: int | None = None,
) -> pd.Series:
    """Compute absolute price changes over a configurable number of observations."""
    days = _resolve_days(days, periods)
    numeric_prices = _as_numeric_series(prices)

    returns = numeric_prices.diff(periods=days)
    return _apply_overlap_filter(returns, days, overlapping)


def log_returns(
    prices: pd.Series,
    days: int = 1,
    overlapping: bool = True,
    *,
    periods: int | None = None,
) -> pd.Series:
    """Compute log returns over a configurable number of observations."""
    days = _resolve_days(days, periods)
    numeric_prices = _as_numeric_series(prices)

    with np.errstate(divide="ignore", invalid="ignore"):
        returns = np.log(numeric_prices / numeric_prices.shift(days))
    returns = returns.replace([np.inf, -np.inf], np.nan)
    return _apply_overlap_filter(returns, days, overlapping)


abs_return = abs_returns
log_return = log_returns


def cumulative_return(
    prices: pd.Series,
    *,
    start_obs: Hashable | None = None,
    end_obs: Hashable | None = None,
    return_type: ReturnType = "rel",
) -> pd.Series:
    """Compute cumulative returns using the requested return convention.

    ``start_obs`` and ``end_obs`` can be integer positions or index labels.
    If omitted, the first and last observations are used.
    """
    return_type = _validate_return_type(return_type)
    numeric_prices = _as_numeric_series(prices)

    if numeric_prices.empty:
        return pd.Series(np.nan, index=numeric_prices.index, name=numeric_prices.name)

    start_position = _get_observation_position(numeric_prices, start_obs, 0)
    end_position = _get_observation_position(numeric_prices, end_obs, len(numeric_prices) - 1)
    if start_position < 0:
        start_position += len(numeric_prices)
    if end_position < 0:
        end_position += len(numeric_prices)
    if (
        start_position < 0
        or end_position < 0
        or start_position >= len(numeric_prices)
        or end_position >= len(numeric_prices)
    ):
        raise IndexError("start_obs and end_obs must be valid observation positions")
    if start_position > end_position:
        raise ValueError("start_obs must be before or equal to end_obs")

    sliced_prices = numeric_prices.iloc[start_position : end_position + 1]
    base_price = sliced_prices.iloc[0]
    if pd.isna(base_price):
        return pd.Series(np.nan, index=sliced_prices.index, name=sliced_prices.name)
    if return_type in {"rel", "log"} and base_price == 0:
        return pd.Series(np.nan, index=sliced_prices.index, name=sliced_prices.name)

    if return_type == "abs":
        returns = sliced_prices - base_price
    elif return_type == "log":
        with np.errstate(divide="ignore", invalid="ignore"):
            returns = np.log(sliced_prices / base_price)
    else:
        returns = (sliced_prices / base_price) - 1

    returns = returns.replace([np.inf, -np.inf], np.nan)
    return returns
