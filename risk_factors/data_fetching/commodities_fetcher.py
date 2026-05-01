"""Commodities data fetcher (Oil, Gold, etc)."""

import yfinance as yf
import pandas as pd
from datetime import datetime
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)

# Commodity tickers
COMMODITY_TICKERS = {
    "Brent Crude": "BZ=F",          # Brent oil futures
    "Gold": "GC=F",                 # Gold futures
    "Natural Gas": "NG=F",          # Natural gas
    "Silver": "SI=F",               # Silver
}


class CommoditiesFetcher:
    """Fetch commodity prices."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.commodities = COMMODITY_TICKERS

    def fetch_all(self):
        """Fetch all commodity prices and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "commodities": {}}

        for name, ticker in self.commodities.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")

                if not hist.empty:
                    price = hist["Close"].iloc[-1]
                    results["commodities"][name] = float(price)
                    logger.info(f"{name}: {price:.2f}")
                else:
                    logger.warning(f"No data received for {name}")
                    results["commodities"][name] = None
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["commodities"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's commodities snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/commodities_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["commodities"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Commodities saved to {filepath}")
        return filepath
