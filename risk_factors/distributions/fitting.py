"""Distribution fitting helpers for P&L and return series."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, pi, sqrt
from statistics import NormalDist
from typing import Literal

import numpy as np
import pandas as pd
from scipy import stats


DistributionName = Literal["normal", "student_t"]
_DEFAULT_STUDENT_T_DF = 30.0
_MAX_STUDENT_T_DF = 1_000_000.0


def _validate_probability(probability: float) -> float:
    if not 0 < probability < 1:
        raise ValueError("probability must be between 0 and 1")
    return probability


def _to_numeric_observations(values: pd.Series, name: str) -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    return pd.to_numeric(values, errors="coerce").dropna()


@dataclass(frozen=True)
class FittedDistribution:
    """A fitted univariate distribution for generic numeric observations.

    The observations may be P&Ls, returns, or other risk-factor shocks. This
    class does not impose a sign convention; callers decide how to interpret
    quantiles or simulations as losses, returns, or scenario shocks.
    """

    distribution: DistributionName
    mean: float
    volatility: float
    sample_size: int
    source_name: str | None = None
    df: float | None = None
    scale_parameter: float | None = None

    @property
    def loc(self) -> float:
        """Location parameter alias for the fitted mean."""
        return self.mean

    @property
    def scale(self) -> float:
        """Scale parameter for the fitted distribution."""
        if self.scale_parameter is not None:
            return self.scale_parameter
        return self.volatility

    @property
    def parameters(self) -> dict[str, float]:
        """Return fitted distribution parameters."""
        parameters = {"loc": self.loc, "scale": self.scale}
        if self.df is not None:
            parameters["df"] = self.df
        return parameters

    def _has_fitted_volatility(self) -> bool:
        return not pd.isna(self.volatility)

    def quantile(self, probability: float) -> float:
        """Return the fitted distribution quantile at the requested probability."""
        probability = _validate_probability(probability)
        if pd.isna(self.mean) or not self._has_fitted_volatility():
            return float("nan")
        if self.volatility == 0:
            return self.mean
        if self.distribution == "student_t":
            return float(stats.t.ppf(probability, df=self._student_t_df(), loc=self.loc, scale=self.scale))
        return float(NormalDist(mu=self.mean, sigma=self.volatility).inv_cdf(probability))

    def cdf(self, value: float) -> float:
        """Return the fitted cumulative probability at ``value``."""
        if pd.isna(self.mean) or not self._has_fitted_volatility():
            return float("nan")
        if self.volatility == 0:
            return float(value >= self.mean)
        if self.distribution == "student_t":
            return float(stats.t.cdf(value, df=self._student_t_df(), loc=self.loc, scale=self.scale))
        return float(NormalDist(mu=self.mean, sigma=self.volatility).cdf(value))

    def pdf(self, value: float) -> float:
        """Return the fitted probability density at ``value``."""
        if pd.isna(self.mean) or not self._has_fitted_volatility():
            return float("nan")
        if self.volatility == 0:
            return float("inf") if value == self.mean else 0.0
        if self.distribution == "student_t":
            return float(stats.t.pdf(value, df=self._student_t_df(), loc=self.loc, scale=self.scale))
        z_score = (value - self.mean) / self.volatility
        return float(exp(-(z_score**2) / 2) / (self.volatility * (2 * pi) ** 0.5))

    def _student_t_df(self) -> float:
        if self.df is None:
            raise ValueError("student_t distribution requires df")
        return self.df

    def simulate(
        self,
        n_scenarios: int,
        *,
        seed: int | None = None,
        name: str | None = None,
    ) -> pd.Series:
        """Generate Monte Carlo scenarios from the fitted distribution."""
        if not isinstance(n_scenarios, int):
            raise TypeError("n_scenarios must be an integer")
        if n_scenarios < 1:
            raise ValueError("n_scenarios must be greater than or equal to 1")

        if pd.isna(self.mean) or not self._has_fitted_volatility():
            scenarios = np.full(n_scenarios, float("nan"), dtype=float)
        elif self.volatility == 0:
            scenarios = np.full(n_scenarios, self.mean, dtype=float)
        else:
            rng = np.random.default_rng(seed)
            if self.distribution == "student_t":
                scenarios = self.loc + self.scale * rng.standard_t(
                    df=self._student_t_df(),
                    size=n_scenarios,
                )
            else:
                scenarios = rng.normal(
                    loc=self.mean,
                    scale=self.volatility,
                    size=n_scenarios,
                )

        series_name = name if name is not None else self.source_name
        return pd.Series(scenarios, name=series_name)


def fit_normaldist_distribution(
    values: pd.Series,
    *,
    name: str = "values",
) -> FittedDistribution:
    """Fit a normal distribution to P&L, return, or shock observations."""
    observations = _to_numeric_observations(values, name)
    if observations.empty:
        return FittedDistribution(
            distribution="normal",
            mean=float("nan"),
            volatility=float("nan"),
            sample_size=0,
            source_name=values.name,
        )

    return FittedDistribution(
        distribution="normal",
        mean=float(observations.mean()),
        volatility=float(observations.std(ddof=1)),
        sample_size=int(observations.size),
        source_name=observations.name,
    )


def fit_student_t_distribution(
    values: pd.Series,
    *,
    name: str = "values",
) -> FittedDistribution:
    """Fit a Student-t distribution to P&L, return, or shock observations.

    The degrees of freedom are estimated from sample excess kurtosis using the
    Student-t relationship ``excess kurtosis = 6 / (df - 4)``. If the sample
    does not show positive excess kurtosis, the fit uses a large ``df`` so the
    distribution behaves close to normal while keeping the Student-t API.
    """
    observations = _to_numeric_observations(values, name)
    if observations.empty:
        return FittedDistribution(
            distribution="student_t",
            mean=float("nan"),
            volatility=float("nan"),
            sample_size=0,
            source_name=values.name,
            df=float("nan"),
            scale_parameter=float("nan"),
        )

    mean = float(observations.mean())
    volatility = float(observations.std(ddof=1))
    df = _estimate_student_t_df(observations)
    scale_parameter = _student_t_scale_from_volatility(volatility, df)

    return FittedDistribution(
        distribution="student_t",
        mean=mean,
        volatility=volatility,
        sample_size=int(observations.size),
        source_name=observations.name,
        df=df,
        scale_parameter=scale_parameter,
    )


def fit_distribution(
    values: pd.Series,
    *,
    distribution: DistributionName = "normal",
    name: str = "values",
) -> FittedDistribution:
    """Fit a supported distribution to P&L, return, or shock observations."""
    if distribution == "normal":
        return fit_normaldist_distribution(values, name=name)
    if distribution == "student_t":
        return fit_student_t_distribution(values, name=name)
    raise ValueError("distribution must be 'normal' or 'student_t'")


def _estimate_student_t_df(observations: pd.Series) -> float:
    excess_kurtosis = float(observations.kurt())
    if not isfinite(excess_kurtosis) or excess_kurtosis <= 0:
        return _MAX_STUDENT_T_DF

    estimated_df = 6.0 / excess_kurtosis + 4.0
    if not isfinite(estimated_df):
        return _DEFAULT_STUDENT_T_DF
    return float(max(estimated_df, 4.000001))


def _student_t_scale_from_volatility(volatility: float, df: float) -> float:
    if pd.isna(volatility):
        return float("nan")
    if volatility == 0:
        return 0.0
    return float(volatility * sqrt((df - 2.0) / df))
