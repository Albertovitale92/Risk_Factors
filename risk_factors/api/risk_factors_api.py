"""Public API for risk-factor data and transformations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Literal

import pandas as pd

from risk_factors.data_fetching.local_store import (
    load_local_levels,
    save_local_levels,
    update_local_levels,
)
from risk_factors.data_fetching.interest_rates_fetcher import (
    EUR_AAA_YIELD_CURVE_SERIES,
    USD_TREASURY_CURVE_SERIES,
    fetch_ecb_mmsr_ois_curve,
    fetch_ecb_series,
    fetch_fred_series,
)
from risk_factors.curves import bootstrap_ecb_ois_zero_curve
from risk_factors.transformations import (
    abs_return,
    correlation_matrix,
    log_return,
    rel_returns,
    rolling_volatility,
)
from risk_factors.utils import get_logger


ReturnMethod = Literal["rel", "abs", "log"]

logger = get_logger(__name__)

EQUITY_TICKERS = {
    "S&P 500": "^GSPC",
    "EuroStoxx 50": "^STOXX50E",
    "FTSE MIB": "FTSEMIB.MI",
    "VIX": "^VIX",
}

FX_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "EUR/GBP": "EURGBP=X",
    "USD/JPY": "USDJPY=X",
    "GBP/USD": "GBPUSD=X",
}

CREDIT_TICKERS = {
    "iTraxx Europe Main": "^ITRXEB",
    "iTraxx Crossover": "^ITRXCBX",
    "HY OAS": "^VIXV",
    "Investment Grade": "LQD",
    "High Yield": "HYG",
    "EUR Bond Index": "VEUR",
}

COMMODITY_TICKERS = {
    "Brent Crude": "BZ=F",
    "Gold": "GC=F",
    "Natural Gas": "NG=F",
    "Silver": "SI=F",
}


def _as_list(values: str | Iterable[str]) -> list[str]:
    if isinstance(values, str):
        return [values]
    return list(values)


def _resolve_tickers(values: str | Iterable[str], mapping: dict[str, str]) -> dict[str, str]:
    resolved = {}
    for value in _as_list(values):
        resolved[value] = mapping.get(value, value)
    return resolved


def _download_close_prices(
    tickers: str | Iterable[str],
    start,
    end,
    mapping: dict[str, str],
) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("yfinance is required to fetch market data") from exc

    resolved_tickers = _resolve_tickers(tickers, mapping)
    data = yf.download(
        list(resolved_tickers.values()),
        start=pd.to_datetime(start).strftime("%Y-%m-%d"),
        end=pd.to_datetime(end).strftime("%Y-%m-%d"),
        progress=False,
        interval="1d",
    )

    if data.empty:
        return pd.DataFrame(columns=list(resolved_tickers))

    if isinstance(data.columns, pd.MultiIndex):
        close_prices = data["Close"]
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame()
    else:
        close_prices = data[["Close"]].copy()
        if len(resolved_tickers) == 1:
            close_prices.columns = list(resolved_tickers)

    ticker_to_name = {ticker: name for name, ticker in resolved_tickers.items()}
    close_prices = close_prices.rename(columns=ticker_to_name)
    return close_prices.reindex(columns=list(resolved_tickers))


def _apply_return_function(data: pd.Series | pd.DataFrame, function, **kwargs):
    if isinstance(data, pd.Series):
        return function(data, **kwargs)
    if isinstance(data, pd.DataFrame):
        return data.apply(lambda column: function(column, **kwargs))
    raise TypeError("data must be a pandas Series or DataFrame")


def get_equity_data(tickers, start, end) -> pd.DataFrame:
    """Fetch equity price history for tickers or configured equity names."""
    return _download_close_prices(tickers, start, end, EQUITY_TICKERS)


def get_fx_data(pairs, start, end) -> pd.DataFrame:
    """Fetch FX rate history for pairs or configured FX names."""
    return _download_close_prices(pairs, start, end, FX_PAIRS)


def get_rates_curve(curve_name: str, date) -> pd.DataFrame:
    """Fetch an interest-rate curve for a specific date."""
    curve_key = curve_name.strip().lower()
    target_date = pd.to_datetime(date)

    if curve_key in {"usd", "usd_treasury", "us_treasury", "treasury"}:
        rows = []
        for tenor, series_id in USD_TREASURY_CURVE_SERIES.items():
            series = fetch_fred_series(series_id, end_date=target_date)
            if series.empty:
                value = None
                value_date = pd.NaT
            else:
                last_row = series[series["date"] <= target_date].tail(1)
                value = last_row["value"].iloc[0] if not last_row.empty else None
                value_date = last_row["date"].iloc[0] if not last_row.empty else pd.NaT
            rows.append({"curve": curve_name, "tenor": tenor, "date": value_date, "value": value})
        return pd.DataFrame(rows)

    if curve_key in {"eur_aaa", "eur", "euro_aaa"}:
        rows = []
        for tenor, series_key in EUR_AAA_YIELD_CURVE_SERIES.items():
            series = fetch_ecb_series(series_key, end_date=target_date)
            last_row = series[series["date"] <= target_date].tail(1)
            rows.append(
                {
                    "curve": curve_name,
                    "tenor": tenor,
                    "date": last_row["date"].iloc[0] if not last_row.empty else pd.NaT,
                    "value": last_row["value"].iloc[0] if not last_row.empty else None,
                }
            )
        return pd.DataFrame(rows)

    if curve_key in {"ecb_ois", "ois", "eur_ois"}:
        curve = fetch_ecb_mmsr_ois_curve(end_date=target_date)
        curve = curve[curve["date"] <= target_date].sort_values("date").groupby("tenor").tail(1)
        curve = curve.rename(columns={"metric": "curve_point"})
        curve.insert(0, "curve", curve_name)
        return curve[["curve", "curve_point", "tenor", "date", "value"]]

    raise ValueError("curve_name must be one of 'usd_treasury', 'eur_aaa', or 'ecb_ois'")


def get_ecb_ois_zero_curve(date, *, mode: str = "par") -> pd.DataFrame:
    """Fetch the ECB MMSR OIS curve for a date and build an approximate zero curve."""
    ois_curve = get_rates_curve("ecb_ois", date)
    if ois_curve.empty:
        return pd.DataFrame(
            columns=[
                "tenor",
                "maturity_years",
                "par_rate",
                "discount_factor",
                "zero_rate_continuous",
                "zero_rate_annual",
            ]
        )
    return bootstrap_ecb_ois_zero_curve(ois_curve, mode=mode)


def get_credit_spreads(issuers, start, end) -> pd.DataFrame:
    """Fetch credit spread/proxy history for issuers or configured credit names."""
    return _download_close_prices(issuers, start, end, CREDIT_TICKERS)


def get_commodities_data(assets, start, end) -> pd.DataFrame:
    """Fetch commodity price history for assets or configured commodity names."""
    return _download_close_prices(assets, start, end, COMMODITY_TICKERS)


def get_returns(
    data: pd.Series | pd.DataFrame,
    method: ReturnMethod = "rel",
    *,
    days: int = 1,
    overlapping: bool = True,
) -> pd.Series | pd.DataFrame:
    """Compute returns from a Series or DataFrame of levels."""
    method_key = method.lower()
    if method_key == "rel":
        return _apply_return_function(data, rel_returns, days=days, overlapping=overlapping)
    if method_key == "abs":
        return _apply_return_function(data, abs_return, days=days, overlapping=overlapping)
    if method_key == "log":
        return _apply_return_function(data, log_return, days=days, overlapping=overlapping)
    raise ValueError("method must be one of 'rel', 'abs', or 'log'")


def get_rolling_vol(
    data: pd.Series | pd.DataFrame,
    window: int = 20,
    *,
    annualization_factor: float | None = None,
) -> pd.Series | pd.DataFrame:
    """Compute rolling volatility for a return Series or DataFrame."""
    return rolling_volatility(
        data,
        window=window,
        annualization_factor=annualization_factor,
    )


def get_correlation_matrix(data: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Compute a correlation matrix for return data."""
    return correlation_matrix(data, method=method)


def get_risk_drivers_snapshot(date=None) -> pd.DataFrame:
    """Return a risk-drivers snapshot for a date.

    If local Parquet history is available, the requested date is loaded from
    that store. For today's date, the function can fetch a fresh market snapshot.
    """
    target_date = pd.to_datetime(date or datetime.now().date()).strftime("%Y-%m-%d")

    historical_data = load_local_levels()
    if not historical_data.empty:
        match = historical_data[historical_data.index.strftime("%Y-%m-%d") == target_date]
        if not match.empty:
            return match.reset_index()

    from risk_factors.data_fetching.historical_fetcher import HistoricalDataFetcher

    historical = HistoricalDataFetcher()
    legacy_historical_data = historical.load_historical_data()
    if not legacy_historical_data.empty and "date" in legacy_historical_data.columns:
        match = legacy_historical_data[legacy_historical_data["date"].astype(str) == target_date]
        if not match.empty:
            return match.reset_index(drop=True)

    today = datetime.now().strftime("%Y-%m-%d")
    if target_date != today:
        raise ValueError(
            f"No local historical snapshot found for {target_date}. "
            "Fetch or load historical data before requesting past snapshots."
        )

    snapshot = {}
    from risk_factors.data_fetching.commodities_fetcher import CommoditiesFetcher
    from risk_factors.data_fetching.credit_fetcher import CreditFetcher
    from risk_factors.data_fetching.equity_fetcher import EquityFetcher
    from risk_factors.data_fetching.fx_fetcher import FXFetcher
    from risk_factors.data_fetching.interest_rates_fetcher import InterestRateFetcher

    for key, fetcher in {
        "equities": EquityFetcher(),
        "forex": FXFetcher(),
        "credit": CreditFetcher(),
        "commodities": CommoditiesFetcher(),
        "interest_rates": InterestRateFetcher(),
    }.items():
        data = fetcher.fetch_all()
        snapshot.update(data.get(key, {}))

    return pd.DataFrame([{"date": today, **snapshot}])
