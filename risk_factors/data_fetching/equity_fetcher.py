"""Equity indices data fetcher (S&P 500, NASDAQ, etc)."""
import yfinance as yf
import pandas as pd
from datetime import datetime
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)

# Major equity indices
EQUITY_TICKERS = {
    "S&P 500": "^GSPC",
    "EuroStoxx 50": "^STOXX50E",
    "FTSE MIB": "FTSEMIB.MI",
    "VIX": "^VIX",  # Equity volatility index
}


class EquityFetcher:
    """Fetch equity market indices."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tickers = EQUITY_TICKERS

    def fetch_all(self):
        """Fetch all equity indices and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "equities": {}}

        for name, ticker in self.tickers.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                # Use Ticker API instead of download for more reliable data extraction
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")
                if not hist.empty:
                    close_price = hist["Close"].iloc[-1]
                    results["equities"][name] = float(close_price)
                    logger.info(f"{name}: {close_price:.2f}")
                else:
                    logger.warning(f"No data received for {name}")
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["equities"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's equity snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/equities_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["equities"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Equities saved to {filepath}")
        return filepath
