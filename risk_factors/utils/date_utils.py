"""Date handling helpers used across the library."""

from __future__ import annotations

import pandas as pd


DateLike = str | pd.Timestamp


def to_datetime(values) -> pd.Series | pd.Timestamp | pd.DatetimeIndex:
    """Convert scalar or array-like values to pandas datetime objects."""
    return pd.to_datetime(values)


def get_business_days(start: DateLike, end: DateLike) -> pd.DatetimeIndex:
    """Return business days between start and end, inclusive."""
    return pd.bdate_range(start=pd.Timestamp(start), end=pd.Timestamp(end))


def shift_business_days(date: DateLike, n: int) -> pd.Timestamp:
    """Shift a date by n business days."""
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    return pd.Timestamp(date) + pd.offsets.BusinessDay(n)


def get_month_end(date: DateLike) -> pd.Timestamp:
    """Return the month-end date for the given date."""
    return pd.Timestamp(date) + pd.offsets.MonthEnd(0)


def get_quarter_end(date: DateLike) -> pd.Timestamp:
    """Return the quarter-end date for the given date."""
    return pd.Timestamp(date) + pd.offsets.QuarterEnd(0)
