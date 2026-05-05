"""Central bank rates and remuneration curve management."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import pandas as pd


class CentralBankRate:
    """Represents a central bank administered rate (e.g., ECB deposit facility rate)."""

    def __init__(
        self,
        rate_name: str,
        rate_value: float,
        currency: str = "EUR",
        rate_type: Literal["deposit_facility", "lending_facility", "main_refinancing"] = "deposit_facility",
        as_of_date: datetime | None = None,
        data_source: str = "ECB",
    ):
        """Initialize a central bank rate.

        Args:
            rate_name: Human-readable name (e.g., "ECB Deposit Facility Rate").
            rate_value: Rate in decimal form (e.g., 0.035 for 3.5%).
            currency: Currency code (default "EUR").
            rate_type: Type of facility (deposit, lending, or main refinancing).
            as_of_date: Date the rate was set (default today).
            data_source: Source of the rate (default "ECB").
        """
        self.rate_name = rate_name
        self.rate_value = rate_value
        self.currency = currency
        self.rate_type = rate_type
        self.as_of_date = as_of_date or datetime.now()
        self.data_source = data_source

    def to_dict(self) -> dict:
        """Convert to dictionary for easy serialization."""
        return {
            "rate_name": self.rate_name,
            "rate_value": self.rate_value,
            "currency": self.currency,
            "rate_type": self.rate_type,
            "as_of_date": self.as_of_date.strftime("%Y-%m-%d"),
            "data_source": self.data_source,
        }

    def __repr__(self) -> str:
        return (
            f"CentralBankRate(name={self.rate_name!r}, value={self.rate_value:.4f}, "
            f"currency={self.currency}, type={self.rate_type})"
        )


def get_ecb_rates_snapshot(
    deposit_facility_rate: float,
    lending_facility_rate: float,
    main_refinancing_rate: float | None = None,
    as_of_date: datetime | None = None,
) -> dict[str, CentralBankRate]:
    """Snapshot of ECB key rates at a point in time.

    Args:
        deposit_facility_rate: ECB deposit facility rate (what the ECB pays banks).
        lending_facility_rate: ECB marginal lending facility rate (what banks pay ECB).
        main_refinancing_rate: ECB main refinancing rate (if available).
        as_of_date: Date of snapshot.

    Returns:
        Dictionary of CentralBankRate objects keyed by rate name.
    """
    as_of = as_of_date or datetime.now()
    rates = {
        "ecb_deposit_facility": CentralBankRate(
            rate_name="ECB Deposit Facility Rate (DFR)",
            rate_value=deposit_facility_rate,
            currency="EUR",
            rate_type="deposit_facility",
            as_of_date=as_of,
        ),
        "ecb_lending_facility": CentralBankRate(
            rate_name="ECB Marginal Lending Facility Rate (MLF)",
            rate_value=lending_facility_rate,
            currency="EUR",
            rate_type="lending_facility",
            as_of_date=as_of,
        ),
    }
    if main_refinancing_rate is not None:
        rates["ecb_main_refinancing"] = CentralBankRate(
            rate_name="ECB Main Refinancing Rate (MRR)",
            rate_value=main_refinancing_rate,
            currency="EUR",
            rate_type="main_refinancing",
            as_of_date=as_of,
        )
    return rates


def compute_opportunity_cost_of_excess_liquidity(
    balance_eur_m: float,
    ecb_rate: float,
    market_rate: float,
    annual: bool = True,
) -> dict[str, float]:
    """Calculate opportunity cost or benefit of holding excess liquidity.

    This is a learning exercise: if the bank holds liquidity at the ECB
    (earning ECB DFR), what does it forgo by not lending at the market rate?

    Args:
        balance_eur_m: Excess balance in EUR millions.
        ecb_rate: ECB deposit facility rate (what you earn).
        market_rate: Market rate (e.g., ESTR, what you could earn lending out).
        annual: If True, return annual amounts; if False, daily.

    Returns:
        Dictionary with:
        - spread_bps: Spread in basis points.
        - annual_interest_at_ecb_rate: Interest earned at ECB rate.
        - annual_interest_at_market_rate: Interest if lent at market rate.
        - opportunity_cost: Annual foregone profit (if market > ECB).
        - frequency: "annual" or "daily".
    """
    spread = market_rate - ecb_rate
    spread_bps = spread * 10000

    annual_at_ecb = balance_eur_m * ecb_rate
    annual_at_market = balance_eur_m * market_rate
    opportunity_cost = annual_at_market - annual_at_ecb

    if not annual:
        annual_at_ecb /= 365
        annual_at_market /= 365
        opportunity_cost /= 365
        frequency = "daily"
    else:
        frequency = "annual"

    return {
        "spread_bps": spread_bps,
        "annual_interest_at_ecb_rate": annual_at_ecb,
        "annual_interest_at_market_rate": annual_at_market,
        "opportunity_cost": opportunity_cost,
        "frequency": frequency,
    }


def create_central_bank_remuneration_curve(
    dfr: float,
    as_of_date: datetime | None = None,
) -> pd.DataFrame:
    """Create a simplified central bank remuneration curve (overnight only).

    The central bank remuneration curve is trivial: just the overnight deposit
    facility rate. This function returns it in a standardized format for consistency
    with other curve constructors.

    Args:
        dfr: ECB deposit facility rate (in decimal, e.g., 0.035).
        as_of_date: Date of the rate.

    Returns:
        DataFrame with columns: tenor, maturity_years, rate, curve_type.
    """
    as_of = as_of_date or datetime.now()
    return pd.DataFrame(
        {
            "tenor": ["1D"],
            "maturity_years": [1 / 365.0],
            "rate": [dfr],
            "curve_type": ["central_bank_remuneration"],
            "as_of_date": [as_of.strftime("%Y-%m-%d")],
        }
    )

