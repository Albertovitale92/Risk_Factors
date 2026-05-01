"""Correlation transformations for return data."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd


CorrelationMethod = Literal["pearson", "spearman", "kendall"]
TailType = Literal["lower", "upper", "both"]


def _validate_returns_frame(returns: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a pandas DataFrame")
    return returns.apply(pd.to_numeric, errors="coerce")


def _validate_return_series(values: pd.Series, name: str) -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    return pd.to_numeric(values, errors="coerce")


def correlation_matrix(
    returns: pd.DataFrame,
    *,
    method: CorrelationMethod = "pearson",
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute the correlation matrix for a DataFrame of returns."""
    numeric_returns = _validate_returns_frame(returns)
    return numeric_returns.corr(method=method, min_periods=min_periods)


def pearson_correlation(
    returns: pd.DataFrame,
    *,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute the Pearson correlation matrix for a DataFrame of returns."""
    return correlation_matrix(returns, method="pearson", min_periods=min_periods)


def spearman_correlation(
    returns: pd.DataFrame,
    *,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute the Spearman rank correlation matrix for a DataFrame of returns."""
    return correlation_matrix(returns, method="spearman", min_periods=min_periods)


def kendall_correlation(
    returns: pd.DataFrame,
    *,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute the Kendall rank correlation matrix for a DataFrame of returns."""
    return correlation_matrix(returns, method="kendall", min_periods=min_periods)


def pairwise_correlation(
    x: pd.Series,
    y: pd.Series,
    method: CorrelationMethod = "pearson",
) -> pd.DataFrame:
    """Compute the correlation between two return Series."""
    x = _validate_return_series(x, "x")
    y = _validate_return_series(y, "y")

    aligned = pd.concat([x, y], axis=1, join="inner")
    aligned = aligned.dropna()
    correlation = aligned.iloc[:, 0].corr(aligned.iloc[:, 1], method=method)

    return pd.DataFrame(
        [
            {
                "x": x.name,
                "y": y.name,
                "method": method,
                "correlation": correlation,
                "n_obs": len(aligned),
            }
        ]
    )


def tail_correlation(
    returns: pd.DataFrame,
    quantile: float = 0.95,
    *,
    tail: TailType = "lower",
    method: CorrelationMethod = "pearson",
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute correlations using only observations in the selected tail."""
    if not 0 < quantile < 1:
        raise ValueError("quantile must be between 0 and 1")
    if tail not in {"lower", "upper", "both"}:
        raise ValueError("tail must be one of 'lower', 'upper', or 'both'")

    numeric_returns = _validate_returns_frame(returns)

    lower_threshold = numeric_returns.quantile(1 - quantile)
    upper_threshold = numeric_returns.quantile(quantile)
    if tail == "lower":
        tail_mask = numeric_returns.le(lower_threshold).any(axis=1)
    elif tail == "upper":
        tail_mask = numeric_returns.ge(upper_threshold).any(axis=1)
    else:
        tail_mask = numeric_returns.le(lower_threshold).any(axis=1)
        tail_mask |= numeric_returns.ge(upper_threshold).any(axis=1)

    return numeric_returns.loc[tail_mask].corr(method=method, min_periods=min_periods)


def partial_correlation(returns: pd.DataFrame) -> pd.DataFrame:
    """Compute the linear partial correlation matrix for return columns."""
    numeric_returns = _validate_returns_frame(returns).dropna()
    corr = numeric_returns.corr()
    precision = np.linalg.pinv(corr.to_numpy(dtype=float))
    diagonal = np.sqrt(np.diag(precision))
    partial = -precision / np.outer(diagonal, diagonal)
    np.fill_diagonal(partial, 1.0)

    return pd.DataFrame(partial, index=corr.index, columns=corr.columns)
