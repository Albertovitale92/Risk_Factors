"""Credit indices data fetcher (iTraxx indices)."""
import yfinance as yf
import pandas as pd
from datetime import datetime
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)

# iTraxx and credit indices
CREDIT_TICKERS = {
    "iTraxx Europe Main": "^ITRXEB",    # iTraxx Europe
    "iTraxx Crossover": "^ITRXCBX",     # iTraxx Crossover
    "HY OAS": "^VIXV",                  # Proxy: VIX volatility
}

# Alternative tickers that might work on Yahoo Finance
ALT_CREDIT_TICKERS = {
    "iTraxx Europe Main": "ITRX.L",     # Alternative ticker
    "iTraxx Crossover": "ITXC.L",       # Alternative ticker
    "High Yield Spread": "HYG",         # High Yield ETF proxy
}


class CreditFetcher:
    """Fetch credit market indices (spreads, bond ETFs)."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.indices = {
            "VIX": "^VIX",                        # Volatility Index
            "Investment Grade": "LQD",            # iShares Investment Grade Corporate Bond ETF
            "High Yield": "HYG",                  # iShares High Yield Corporate Bond ETF
            "EUR Bond Index": "VEUR",             # Vanguard FTSE All-World UCITS ETF (EUR bond market indicator)
        }

    def fetch_all(self):
        """Fetch all credit indices and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "credit": {}}

        for name, ticker in self.indices.items():
            try:
                logger.info(f"Fetching {name} ({ticker})...")
                tick = yf.Ticker(ticker)
                hist = tick.history(period="1d")

                if not hist.empty:
                    value = hist["Close"].iloc[-1]
                    results["credit"][name] = float(value)
                    logger.info(f"{name}: {value:.2f}")
                else:
                    logger.warning(f"No data received for {name}")
                    results["credit"][name] = None
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                results["credit"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's credit indices snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/credit_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["credit"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Credit indices saved to {filepath}")
        return filepath

