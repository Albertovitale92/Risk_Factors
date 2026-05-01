"""Alignment helpers for time series data."""

from __future__ import annotations

import pandas as pd


PandasObject = pd.Series | pd.DataFrame


def _validate_pandas_object(values: PandasObject) -> PandasObject:
    if not isinstance(values, (pd.Series, pd.DataFrame)):
        raise TypeError("all inputs must be pandas Series or DataFrame objects")
    return values


def align_time_series(*values: PandasObject) -> tuple[PandasObject, ...]:
    """Align Series/DataFrames on their common index using an inner join."""
    if not values:
        raise ValueError("at least one Series or DataFrame is required")

    validated_values = tuple(_validate_pandas_object(value) for value in values)
    common_index = validated_values[0].index
    for value in validated_values[1:]:
        common_index = common_index.intersection(value.index)

    return tuple(value.loc[common_index] for value in validated_values)


def align_to_common_index(*values: PandasObject) -> tuple[PandasObject, ...]:
    """Alias for align_time_series."""
    return align_time_series(*values)
