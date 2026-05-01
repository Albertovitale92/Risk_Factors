"""Cryptocurrency data fetcher (Bitcoin, Ethereum, etc)."""
import yfinance as yf
import pandas as pd
from datetime import datetime
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)

# Cryptocurrency tickers
CRYPTO_TICKERS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
}


class CryptoFetcher:
    """Fetch cryptocurrency prices."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.cryptocurrencies = CRYPTO_TICKERS

    def fetch_all(self):
        """Fetch all cryptocurrency prices and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "cryptocurrencies": {}}

        for name, ticker in self.cryptocurrencies.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")

                if not hist.empty:
                    price = hist["Close"].iloc[-1]
                    results["cryptocurrencies"][name] = float(price)
                    logger.info(f"{name}: ${price:.2f}")
                else:
                    logger.warning(f"No data received for {name}")
                    results["cryptocurrencies"][name] = None
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["cryptocurrencies"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's cryptocurrency snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/cryptocurrencies_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["cryptocurrencies"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Cryptocurrencies saved to {filepath}")
        return filepath
