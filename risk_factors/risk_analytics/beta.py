"""Beta analytics for return series."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_numeric_series(values: pd.Series, name: str) -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    return pd.to_numeric(values, errors="coerce")


def compute_beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Compute beta of an asset return series versus a benchmark."""
    asset = _to_numeric_series(asset_returns, "asset_returns")
    benchmark = _to_numeric_series(benchmark_returns, "benchmark_returns")
    aligned = pd.concat([asset, benchmark], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return np.nan

    benchmark_variance = aligned.iloc[:, 1].var(ddof=1)
    if benchmark_variance == 0 or pd.isna(benchmark_variance):
        return np.nan

    covariance = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    return float(covariance / benchmark_variance)


def compute_multi_beta(
    returns_df: pd.DataFrame,
    benchmark_returns: pd.Series,
) -> pd.Series:
    """Compute beta for each return column against a benchmark."""
    if not isinstance(returns_df, pd.DataFrame):
        raise TypeError("returns_df must be a pandas DataFrame")

    benchmark = _to_numeric_series(benchmark_returns, "benchmark_returns")
    return pd.Series(
        {
            column: compute_beta(
                pd.to_numeric(returns_df[column], errors="coerce"),
                benchmark,
            )
            for column in returns_df.columns
        },
        name="beta",
    )
