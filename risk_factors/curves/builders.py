"""Curve construction helpers."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Literal

import pandas as pd


BootstrapMode = Literal["par", "direct"]
RateUnit = Literal["auto", "decimal", "percent"]

_TENOR_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([DWMY])\s*$", re.IGNORECASE)


def tenor_to_years(tenor: str) -> float:
    """Convert a tenor string such as ``3M`` or ``10Y`` to year fractions."""
    match = _TENOR_PATTERN.match(str(tenor))
    if not match:
        raise ValueError(f"Unsupported tenor format: {tenor!r}")

    value = float(match.group(1))
    unit = match.group(2).upper()
    if value <= 0:
        raise ValueError("tenor must be positive")
    if unit == "D":
        return value / 365.0
    if unit == "W":
        return value / 52.0
    if unit == "M":
        return value / 12.0
    return value


def bootstrap_ecb_ois_zero_curve(
    curve: pd.DataFrame | pd.Series | Mapping[str, float],
    *,
    mode: BootstrapMode = "par",
    rate_unit: RateUnit = "auto",
    short_end_cutoff_years: float = 1.0,
    fixed_leg_frequency: int = 1,
) -> pd.DataFrame:
    """Bootstrap an approximate zero curve from ECB MMSR OIS bucket rates.

    ECB MMSR OIS observations are transaction-based weighted-average rates by
    maturity bucket, not guaranteed dealer par swap quotes. The default
    ``mode="par"`` treats them as par OIS fixed rates for curve construction.
    Use ``mode="direct"`` to convert each bucket rate directly into a discount
    factor without par-swap bootstrapping.
    """
    if mode not in {"par", "direct"}:
        raise ValueError("mode must be one of 'par' or 'direct'")
    if rate_unit not in {"auto", "decimal", "percent"}:
        raise ValueError("rate_unit must be one of 'auto', 'decimal', or 'percent'")
    if short_end_cutoff_years <= 0:
        raise ValueError("short_end_cutoff_years must be positive")
    if fixed_leg_frequency <= 0:
        raise ValueError("fixed_leg_frequency must be positive")

    nodes = _normalise_curve_input(curve, rate_unit=rate_unit)
    discount_factors: dict[float, float] = {}
    rows = []

    for tenor, maturity, rate in nodes:
        if mode == "direct" or maturity <= short_end_cutoff_years:
            discount_factor = _simple_discount_factor(rate, maturity)
        else:
            discount_factor = _bootstrap_par_swap_discount_factor(
                par_rate=rate,
                maturity=maturity,
                known_discount_factors=discount_factors,
                fixed_leg_frequency=fixed_leg_frequency,
            )

        discount_factors[maturity] = discount_factor
        rows.append(
            {
                "tenor": tenor,
                "maturity_years": maturity,
                "par_rate": rate,
                "discount_factor": discount_factor,
                "zero_rate_continuous": -math.log(discount_factor) / maturity,
                "zero_rate_annual": discount_factor ** (-1.0 / maturity) - 1.0,
            }
        )

    return pd.DataFrame(rows)


def _normalise_curve_input(
    curve: pd.DataFrame | pd.Series | Mapping[str, float],
    *,
    rate_unit: RateUnit,
) -> list[tuple[str, float, float]]:
    if isinstance(curve, pd.Series):
        frame = curve.rename("value").reset_index()
        frame = frame.rename(columns={frame.columns[0]: "tenor"})
    elif isinstance(curve, Mapping):
        frame = pd.Series(curve, name="value").reset_index()
        frame = frame.rename(columns={"index": "tenor"})
    elif isinstance(curve, pd.DataFrame):
        frame = curve.copy()
    else:
        raise TypeError("curve must be a pandas DataFrame, Series, or mapping")

    if "tenor" not in frame.columns:
        raise ValueError("curve input must contain a 'tenor' column")

    rate_column = _select_rate_column(frame)
    frame = frame[["tenor", rate_column]].rename(columns={rate_column: "par_rate"}).copy()
    frame["par_rate"] = pd.to_numeric(frame["par_rate"], errors="coerce")
    frame = frame.dropna(subset=["tenor", "par_rate"])
    if frame.empty:
        raise ValueError("curve input contains no valid rate observations")

    frame["maturity_years"] = frame["tenor"].map(tenor_to_years)
    frame = frame.sort_values("maturity_years").drop_duplicates("maturity_years", keep="last")
    scale = _rate_scale(frame["par_rate"], rate_unit)
    frame["par_rate"] = frame["par_rate"] * scale

    return [
        (str(row.tenor), float(row.maturity_years), float(row.par_rate))
        for row in frame.itertuples(index=False)
    ]


def _select_rate_column(frame: pd.DataFrame) -> str:
    for column in ("par_rate", "value", "rate"):
        if column in frame.columns:
            return column
    raise ValueError("curve input must contain one of 'par_rate', 'value', or 'rate'")


def _rate_scale(rates: pd.Series, rate_unit: RateUnit) -> float:
    if rate_unit == "decimal":
        return 1.0
    if rate_unit == "percent":
        return 0.01
    return 0.01 if rates.abs().max() > 1.0 else 1.0


def _simple_discount_factor(rate: float, maturity: float) -> float:
    denominator = 1.0 + rate * maturity
    if denominator <= 0:
        raise ValueError("simple discount factor denominator must be positive")
    return 1.0 / denominator


def _bootstrap_par_swap_discount_factor(
    *,
    par_rate: float,
    maturity: float,
    known_discount_factors: dict[float, float],
    fixed_leg_frequency: int,
) -> float:
    payment_times = _payment_times(maturity, fixed_leg_frequency)
    known_times = sorted(known_discount_factors)

    def objective(candidate_discount_factor: float) -> float:
        all_discount_factors = {**known_discount_factors, maturity: candidate_discount_factor}
        annuity = 0.0
        previous_time = 0.0
        for payment_time in payment_times:
            accrual = payment_time - previous_time
            annuity += accrual * _discount_factor_at(
                payment_time,
                all_discount_factors,
                known_times,
                maturity,
                candidate_discount_factor,
            )
            previous_time = payment_time
        return 1.0 - candidate_discount_factor - par_rate * annuity

    lower = 1e-12
    upper = max(2.0, known_discount_factors[max(known_discount_factors)] * 2.0)
    while objective(upper) > 0:
        upper *= 2.0
        if upper > 100.0:
            raise ValueError("could not bracket bootstrapped discount factor")

    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        if objective(midpoint) > 0:
            lower = midpoint
        else:
            upper = midpoint

    return (lower + upper) / 2.0


def _payment_times(maturity: float, fixed_leg_frequency: int) -> list[float]:
    step = 1.0 / fixed_leg_frequency
    times = []
    current = step
    tolerance = 1e-12
    while current < maturity - tolerance:
        times.append(current)
        current += step
    times.append(maturity)
    return times


def _discount_factor_at(
    payment_time: float,
    discount_factors: dict[float, float],
    known_times: list[float],
    maturity: float,
    maturity_discount_factor: float,
) -> float:
    if payment_time in discount_factors:
        return discount_factors[payment_time]

    if payment_time < maturity:
        lower_time = max(time for time in known_times if time < payment_time)
        lower_df = discount_factors[lower_time]
        upper_time = maturity
        upper_df = maturity_discount_factor
        log_df = _linear_interpolate(
            payment_time,
            lower_time,
            math.log(lower_df),
            upper_time,
            math.log(upper_df),
        )
        return math.exp(log_df)

    return maturity_discount_factor


def _linear_interpolate(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
