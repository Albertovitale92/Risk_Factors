"""Rolling transformations for time series."""

from __future__ import annotations

import pandas as pd


PandasObject = pd.Series | pd.DataFrame


def _resolve_window(window: int | None, days: int | None) -> int:
    if window is not None and days is not None:
        raise ValueError("use either window or days, not both")

    resolved_window = window if window is not None else days
    if not isinstance(resolved_window, int):
        raise TypeError("window must be an integer")
    if resolved_window < 1:
        raise ValueError("window must be greater than or equal to 1")
    return resolved_window


def _validate_pandas_object(values: PandasObject) -> PandasObject:
    if not isinstance(values, (pd.Series, pd.DataFrame)):
        raise TypeError("values must be a pandas Series or DataFrame")
    return values


def rolling_mean(
    values: PandasObject,
    window: int | None = None,
    *,
    days: int | None = None,
    min_periods: int | None = None,
) -> PandasObject:
    """Compute a rolling mean for a Series or DataFrame."""
    values = _validate_pandas_object(values)
    window = _resolve_window(window, days)

    return values.rolling(window=window, min_periods=min_periods).mean()


def rolling_volatility(
    values: PandasObject,
    window: int | None = None,
    *,
    days: int | None = None,
    min_periods: int | None = None,
    ddof: int = 1,
    annualization_factor: float | None = None,
) -> PandasObject:
    """Compute rolling volatility for a Series or DataFrame.

    ``annualization_factor`` can be set to values such as 252 for daily data.
    """
    values = _validate_pandas_object(values)
    window = _resolve_window(window, days)

    volatility = values.rolling(window=window, min_periods=min_periods).std(ddof=ddof)
    if annualization_factor is not None:
        volatility = volatility * annualization_factor**0.5
    return volatility


def rolling_correlation(
    left: PandasObject,
    right: PandasObject | None = None,
    window: int | None = None,
    *,
    days: int | None = None,
    min_periods: int | None = None,
    pairwise: bool | None = None,
) -> PandasObject:
    """Compute rolling correlation for Series or DataFrame inputs."""
    left = _validate_pandas_object(left)
    if right is not None:
        right = _validate_pandas_object(right)

    window = _resolve_window(window, days)

    return left.rolling(window=window, min_periods=min_periods).corr(
        other=right,
        pairwise=pairwise,
    )
