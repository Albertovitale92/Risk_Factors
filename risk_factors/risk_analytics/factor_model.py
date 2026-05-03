"""Factor-model analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def ols_factor_exposures(
    returns: pd.Series | pd.DataFrame,
    factors: pd.DataFrame,
) -> pd.DataFrame:
    """Estimate OLS factor exposures for one or more return series."""
    if isinstance(returns, pd.Series):
        returns_df = returns.to_frame(name=returns.name or "returns")
    elif isinstance(returns, pd.DataFrame):
        returns_df = returns.copy()
    else:
        raise TypeError("returns must be a pandas Series or DataFrame")
    if not isinstance(factors, pd.DataFrame):
        raise TypeError("factors must be a pandas DataFrame")

    numeric_returns = returns_df.apply(pd.to_numeric, errors="coerce")
    numeric_factors = factors.apply(pd.to_numeric, errors="coerce")
    aligned = numeric_returns.join(numeric_factors, how="inner").dropna()
    y = aligned[numeric_returns.columns].to_numpy(dtype=float)
    x = aligned[numeric_factors.columns].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(x)), x])

    coefficients = np.linalg.lstsq(x, y, rcond=None)[0]
    index = ["intercept", *numeric_factors.columns]
    return pd.DataFrame(coefficients, index=index, columns=numeric_returns.columns)


def pca_factors(returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Compute PCA factor scores, explained variance ratio, and loadings."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a pandas DataFrame")

    numeric_returns = returns.apply(pd.to_numeric, errors="coerce").dropna()
    centered = numeric_returns - numeric_returns.mean()
    _, singular_values, vt = np.linalg.svd(centered.to_numpy(dtype=float), full_matrices=False)

    scores = centered.to_numpy(dtype=float) @ vt.T
    eigenvalues = singular_values**2 / (len(centered) - 1)
    explained_variance = eigenvalues / eigenvalues.sum()

    component_names = [f"PC{i + 1}" for i in range(len(eigenvalues))]
    scores_df = pd.DataFrame(scores, index=centered.index, columns=component_names)
    explained_variance_series = pd.Series(
        explained_variance,
        index=component_names,
        name="explained_variance_ratio",
    )
    loadings = pd.DataFrame(vt.T, index=numeric_returns.columns, columns=component_names)
    return scores_df, explained_variance_series, loadings


def factor_risk_contribution(
    returns: pd.Series | pd.DataFrame,
    exposures: pd.Series | pd.DataFrame,
    cov_matrix: pd.DataFrame,
) -> pd.Series | pd.DataFrame:
    """Compute variance contribution from factor exposures and covariance."""
    if not isinstance(cov_matrix, pd.DataFrame):
        raise TypeError("cov_matrix must be a pandas DataFrame")

    covariance = cov_matrix.apply(pd.to_numeric, errors="coerce")
    if isinstance(exposures, pd.Series):
        exposure = pd.to_numeric(exposures, errors="coerce").reindex(covariance.index)
        marginal = covariance.to_numpy(dtype=float) @ exposure.to_numpy(dtype=float)
        contribution = exposure.to_numpy(dtype=float) * marginal
        total_variance = contribution.sum()
        if total_variance != 0:
            contribution = contribution / total_variance
        return pd.Series(contribution, index=covariance.index, name="risk_contribution")

    if isinstance(exposures, pd.DataFrame):
        exposure_df = exposures.apply(pd.to_numeric, errors="coerce").reindex(columns=covariance.index)
        rows = {}
        for row_name, row in exposure_df.iterrows():
            rows[row_name] = factor_risk_contribution(returns, row, covariance)
        return pd.DataFrame(rows).T

    raise TypeError("exposures must be a pandas Series or DataFrame")
