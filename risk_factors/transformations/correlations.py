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


def _kendall_tau(x: pd.Series, y: pd.Series) -> float:
    aligned = pd.concat([x, y], axis=1).dropna()
    if len(aligned) < 2:
        return np.nan

    x_values = aligned.iloc[:, 0].to_numpy()
    y_values = aligned.iloc[:, 1].to_numpy()
    concordant = 0
    discordant = 0
    ties_x = 0
    ties_y = 0

    for i in range(len(aligned) - 1):
        for j in range(i + 1, len(aligned)):
            x_diff = np.sign(x_values[i] - x_values[j])
            y_diff = np.sign(y_values[i] - y_values[j])
            if x_diff == 0 and y_diff == 0:
                continue
            if x_diff == 0:
                ties_x += 1
            elif y_diff == 0:
                ties_y += 1
            elif x_diff == y_diff:
                concordant += 1
            else:
                discordant += 1

    denominator = (
        (concordant + discordant + ties_x)
        * (concordant + discordant + ties_y)
    ) ** 0.5
    if denominator == 0:
        return np.nan
    return (concordant - discordant) / denominator


def _kendall_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    columns = list(returns.columns)
    matrix = pd.DataFrame(np.eye(len(columns)), index=columns, columns=columns)
    for left_index, left_column in enumerate(columns):
        for right_column in columns[left_index + 1 :]:
            correlation = _kendall_tau(returns[left_column], returns[right_column])
            matrix.loc[left_column, right_column] = correlation
            matrix.loc[right_column, left_column] = correlation
    return matrix


def correlation_matrix(
    returns: pd.DataFrame,
    *,
    method: CorrelationMethod = "pearson",
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Compute the correlation matrix for a DataFrame of returns."""
    numeric_returns = _validate_returns_frame(returns)
    if method == "kendall":
        return _kendall_correlation_matrix(numeric_returns)
    if min_periods is None:
        return numeric_returns.corr(method=method)
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
    if method == "kendall":
        correlation = _kendall_tau(aligned.iloc[:, 0], aligned.iloc[:, 1])
    else:
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

    tail_returns = numeric_returns.loc[tail_mask]
    if min_periods is None:
        return tail_returns.corr(method=method)
    return tail_returns.corr(method=method, min_periods=min_periods)


def partial_correlation(returns: pd.DataFrame) -> pd.DataFrame:
    """Compute the linear partial correlation matrix for return columns."""
    numeric_returns = _validate_returns_frame(returns).dropna()
    corr = numeric_returns.corr()
    precision = np.linalg.pinv(corr.to_numpy(dtype=float))
    diagonal = np.sqrt(np.diag(precision))
    partial = -precision / np.outer(diagonal, diagonal)
    np.fill_diagonal(partial, 1.0)

    return pd.DataFrame(partial, index=corr.index, columns=corr.columns)
