"""Market and reference data ingestion clients."""

from risk_factors.data_fetching.local_store import (
    DEFAULT_DATA_DIR,
    DEFAULT_LEVELS_PATH,
    DEFAULT_METADATA_PATH,
    load_local_levels,
    load_local_metadata,
    save_local_levels,
    update_local_levels,
)

_LAZY_EXPORTS = {
    "CommoditiesFetcher": "risk_factors.data_fetching.commodities_fetcher",
    "CreditFetcher": "risk_factors.data_fetching.credit_fetcher",
    "CryptoFetcher": "risk_factors.data_fetching.crypto_fetcher",
    "EquityFetcher": "risk_factors.data_fetching.equity_fetcher",
    "FXFetcher": "risk_factors.data_fetching.fx_fetcher",
    "HistoricalDataFetcher": "risk_factors.data_fetching.historical_fetcher",
    "InterestRateFetcher": "risk_factors.data_fetching.interest_rates_fetcher",
    "fetch_ecb_mmsr_ois_curve": "risk_factors.data_fetching.interest_rates_fetcher",
    "fetch_ecb_series": "risk_factors.data_fetching.interest_rates_fetcher",
    "fetch_fred_series": "risk_factors.data_fetching.interest_rates_fetcher",
}

__all__ = [
    "CommoditiesFetcher",
    "CreditFetcher",
    "CryptoFetcher",
    "DEFAULT_DATA_DIR",
    "DEFAULT_LEVELS_PATH",
    "DEFAULT_METADATA_PATH",
    "EquityFetcher",
    "FXFetcher",
    "HistoricalDataFetcher",
    "InterestRateFetcher",
    "fetch_ecb_mmsr_ois_curve",
    "fetch_ecb_series",
    "fetch_fred_series",
    "load_local_levels",
    "load_local_metadata",
    "save_local_levels",
    "update_local_levels",
]


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    module = import_module(_LAZY_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
