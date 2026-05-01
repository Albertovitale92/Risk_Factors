"""FX rates data fetcher (EUR/USD, GBP/USD, etc)."""
import yfinance as yf
import pandas as pd
from datetime import datetime
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)

# FX pairs
FX_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "EUR/GBP": "EURGBP=X",
    "USD/JPY": "USDJPY=X",      # Added for additional context
    "GBP/USD": "GBPUSD=X",      # Added for additional context
}


class FXFetcher:
    """Fetch foreign exchange rate data."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.pairs = FX_PAIRS

    def fetch_all(self):
        """Fetch all FX pairs and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "forex": {}}

        for name, ticker in self.pairs.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")

                if not hist.empty:
                    rate = hist["Close"].iloc[-1]
                    results["forex"][name] = float(rate)
                    logger.info(f"{name}: {rate:.6f}")
                else:
                    logger.warning(f"No data received for {name}")
                    results["forex"][name] = None
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["forex"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's FX snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/forex_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["forex"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"FX rates saved to {filepath}")
        return filepath

