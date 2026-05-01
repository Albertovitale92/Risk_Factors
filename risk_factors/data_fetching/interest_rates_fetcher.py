"""Interest rates and fixed income data fetcher."""
import pandas as pd
from datetime import datetime
from urllib.parse import urlencode
from risk_factors.utils.logger import get_logger

logger = get_logger(__name__)


FRED_BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ECB_BASE_URL = "https://data-api.ecb.europa.eu/service/data"
ECB_EURIBOR_3M_SERIES_KEY = "FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"
ECB_EUR_AAA_CURVE_PREFIX = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM"
ECB_MMSR_OIS_PREFIX = "MMSR.B.U2._X._Z.S1ZV._Z.O._X.WR._X"

USD_TREASURY_CURVE_SERIES = {
    "US 1M Treasury": "DGS1MO",
    "US 3M Treasury": "DGS3MO",
    "US 6M Treasury": "DGS6MO",
    "US 1Y Treasury": "DGS1",
    "US 2Y Treasury": "DGS2",
    "US 3Y Treasury": "DGS3",
    "US 5Y Treasury": "DGS5",
    "US 7Y Treasury": "DGS7",
    "US 10Y Treasury": "DGS10",
    "US 20Y Treasury": "DGS20",
    "US 30Y Treasury": "DGS30",
}

EUR_AAA_YIELD_CURVE_SERIES = {
    "EUR AAA 1Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_1Y",
    "EUR AAA 2Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_2Y",
    "EUR AAA 5Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_5Y",
    "EUR AAA 10Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_10Y",
    "EUR AAA 20Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_20Y",
    "EUR AAA 30Y": f"{ECB_EUR_AAA_CURVE_PREFIX}.SR_30Y",
}

ESTR_REALISED_RATE_SERIES = {
    "ESTR ON": "EST.B.EU000A2X2A25.WT",
    "ESTR 1W Realised": "EST.B.EU000A2QQF16.CR",
    "ESTR 1M Realised": "EST.B.EU000A2QQF24.CR",
    "ESTR 3M Realised": "EST.B.EU000A2QQF32.CR",
    "ESTR 6M Realised": "EST.B.EU000A2QQF40.CR",
    "ESTR 12M Realised": "EST.B.EU000A2QQF57.CR",
}

ECB_MMSR_OIS_CURVE_SERIES = {
    "ECB OIS 1M": f"{ECB_MMSR_OIS_PREFIX}.FC._Z._Z.EUR._Z",
    "ECB OIS 2M": f"{ECB_MMSR_OIS_PREFIX}.FD._Z._Z.EUR._Z",
    "ECB OIS 3M": f"{ECB_MMSR_OIS_PREFIX}.FE._Z._Z.EUR._Z",
    "ECB OIS 6M": f"{ECB_MMSR_OIS_PREFIX}.FF._Z._Z.EUR._Z",
    "ECB OIS 9M": f"{ECB_MMSR_OIS_PREFIX}.FG._Z._Z.EUR._Z",
    "ECB OIS 12M": f"{ECB_MMSR_OIS_PREFIX}.FH._Z._Z.EUR._Z",
    "ECB OIS 2Y": f"{ECB_MMSR_OIS_PREFIX}.FI._Z._Z.EUR._Z",
    "ECB OIS 3Y": f"{ECB_MMSR_OIS_PREFIX}.FJ._Z._Z.EUR._Z",
    "ECB OIS 5Y": f"{ECB_MMSR_OIS_PREFIX}.FK._Z._Z.EUR._Z",
    "ECB OIS 10Y": f"{ECB_MMSR_OIS_PREFIX}.FL._Z._Z.EUR._Z",
}

ECB_MMSR_OIS_MATURITY_CODES = {
    "FC": ("ECB OIS 1M", "1M"),
    "FD": ("ECB OIS 2M", "2M"),
    "FE": ("ECB OIS 3M", "3M"),
    "FF": ("ECB OIS 6M", "6M"),
    "FG": ("ECB OIS 9M", "9M"),
    "FH": ("ECB OIS 12M", "12M"),
    "FI": ("ECB OIS 2Y", "2Y"),
    "FJ": ("ECB OIS 3Y", "3Y"),
    "FK": ("ECB OIS 5Y", "5Y"),
    "FL": ("ECB OIS 10Y", "10Y"),
}


def fetch_fred_series(series_id, start_date=None, end_date=None):
    """Fetch a daily FRED series as a date/value DataFrame."""
    url = f"{FRED_BASE_URL}?id={series_id}"
    df = pd.read_csv(url)

    if "observation_date" in df.columns:
        date_col = "observation_date"
    elif "DATE" in df.columns:
        date_col = "DATE"
    else:
        date_col = df.columns[0]

    value_col = series_id if series_id in df.columns else df.columns[-1]
    df = df.rename(columns={date_col: "date", value_col: "value"})
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"].replace(".", pd.NA), errors="coerce")

    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]

    return df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)


def fetch_ecb_series(series_key, start_date=None, end_date=None, last_n_observations=None):
    """Fetch an ECB Data Portal series as a date/value DataFrame."""
    flow_ref, key = series_key.split(".", 1)
    params = {"format": "csvdata"}
    if start_date:
        params["startPeriod"] = pd.to_datetime(start_date).strftime("%Y-%m")
    if end_date:
        params["endPeriod"] = pd.to_datetime(end_date).strftime("%Y-%m")
    if last_n_observations:
        params["lastNObservations"] = str(last_n_observations)

    url = f"{ECB_BASE_URL}/{flow_ref}/{key}?{urlencode(params)}"
    df = pd.read_csv(url)
    if df.empty:
        return pd.DataFrame(columns=["date", "value"])

    df = df.rename(columns={"TIME_PERIOD": "date", "OBS_VALUE": "value"})
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["date", "value"]].dropna(subset=["value"]).sort_values("date").reset_index(drop=True)


def fetch_ecb_mmsr_ois_curve(start_date=None, end_date=None, last_n_observations=None):
    """Fetch ECB MMSR OIS weighted-average rate buckets in one wildcard request."""
    wildcard_series_key = f"{ECB_MMSR_OIS_PREFIX}.._Z._Z.EUR._Z"
    flow_ref, key = wildcard_series_key.split(".", 1)
    params = {"format": "csvdata"}
    if start_date:
        params["startPeriod"] = pd.to_datetime(start_date).strftime("%Y-%m")
    if end_date:
        params["endPeriod"] = pd.to_datetime(end_date).strftime("%Y-%m")
    if last_n_observations:
        params["lastNObservations"] = str(last_n_observations)

    url = f"{ECB_BASE_URL}/{flow_ref}/{key}?{urlencode(params)}"
    df = pd.read_csv(url)
    if df.empty:
        return pd.DataFrame(columns=["date", "metric", "tenor", "value"])

    df = df.rename(columns={"TIME_PERIOD": "date", "OBS_VALUE": "value"})
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["maturity_code"] = df["KEY"].astype(str).str.split(".").str[11]
    df = df[df["maturity_code"].isin(ECB_MMSR_OIS_MATURITY_CODES)].copy()
    df["metric"] = df["maturity_code"].map(lambda code: ECB_MMSR_OIS_MATURITY_CODES[code][0])
    df["tenor"] = df["maturity_code"].map(lambda code: ECB_MMSR_OIS_MATURITY_CODES[code][1])

    return (
        df[["date", "metric", "tenor", "value"]]
        .dropna(subset=["value"])
        .sort_values(["date", "tenor"])
        .reset_index(drop=True)
    )

class InterestRateFetcher:
    """Fetch interest rate and fixed income data (USD Treasury + EUR rates)."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.us_treasury_curve = USD_TREASURY_CURVE_SERIES
        self.eur_aaa_curve = EUR_AAA_YIELD_CURVE_SERIES
        self.eur_rates = {
            "EURIBOR 3M": ECB_EURIBOR_3M_SERIES_KEY,
        }
        self.estr_realised_rates = ESTR_REALISED_RATE_SERIES
        self.ecb_ois_curve = ECB_MMSR_OIS_CURVE_SERIES

    def fetch_all(self):
        """Fetch all interest rate metrics and return as a dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        results = {"date": today, "interest_rates": {}}

        for name, series_id in self.us_treasury_curve.items():
            try:
                logger.info(f"Fetching {name} from FRED ({series_id})...")
                series = fetch_fred_series(series_id)
                value = series["value"].iloc[-1] if not series.empty else None
                results["interest_rates"][name] = float(value) if value is not None else None
                if value is not None:
                    logger.info(f"✓ {name}: {value:.2f}")
                else:
                    logger.warning(f"⚠️  Could not fetch {name} from FRED")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name} from FRED ({series_id}): {e}")
                results["interest_rates"][name] = None

        for name, series_key in self.eur_rates.items():
            try:
                logger.info(f"Fetching {name} from ECB ({series_key})...")
                series = fetch_ecb_series(series_key, last_n_observations=1)
                value = series["value"].iloc[-1] if not series.empty else None
                results["interest_rates"][name] = float(value) if value is not None else None
                if value is not None:
                    logger.info(f"✓ {name}: {value:.4f}")
                else:
                    logger.warning(f"⚠️  Could not fetch {name} from ECB")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name} from ECB ({series_key}): {e}")
                results["interest_rates"][name] = None

        for name, series_key in self.estr_realised_rates.items():
            try:
                logger.info(f"Fetching {name} from ECB ({series_key})...")
                series = fetch_ecb_series(series_key, last_n_observations=1)
                value = series["value"].iloc[-1] if not series.empty else None
                results["interest_rates"][name] = float(value) if value is not None else None
                if value is not None:
                    logger.info(f"✓ {name}: {value:.4f}")
                else:
                    logger.warning(f"⚠️  Could not fetch {name} from ECB")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name} from ECB ({series_key}): {e}")
                results["interest_rates"][name] = None

        try:
            logger.info("Fetching ECB MMSR OIS curve in one request...")
            ois_curve = fetch_ecb_mmsr_ois_curve(last_n_observations=1)
            ois_by_metric = ois_curve.sort_values("date").groupby("metric").tail(1)
            for name in self.ecb_ois_curve:
                match = ois_by_metric[ois_by_metric["metric"] == name]
                value = match["value"].iloc[-1] if not match.empty else None
                results["interest_rates"][name] = float(value) if value is not None else None
                if value is not None:
                    logger.info(f"✓ {name}: {value:.4f}")
                else:
                    logger.warning(f"⚠️  Could not fetch {name} from ECB MMSR")
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch ECB MMSR OIS curve: {e}")
            for name in self.ecb_ois_curve:
                results["interest_rates"][name] = None

        for name, series_key in self.eur_aaa_curve.items():
            try:
                logger.info(f"Fetching {name} from ECB ({series_key})...")
                series = fetch_ecb_series(series_key, last_n_observations=1)
                value = series["value"].iloc[-1] if not series.empty else None
                results["interest_rates"][name] = float(value) if value is not None else None
                if value is not None:
                    logger.info(f"✓ {name}: {value:.4f}")
                else:
                    logger.warning(f"⚠️  Could not fetch {name} from ECB")
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name} from ECB ({series_key}): {e}")
                results["interest_rates"][name] = None

        return results

    def save_daily_snapshot(self):
        """Save today's interest rate snapshot to CSV."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{self.data_dir}/interest_rates_{today}.csv"

        data = self.fetch_all()
        df = pd.DataFrame([data["interest_rates"]])
        df.insert(0, "date", data["date"])

        df.to_csv(filepath, index=False)
        logger.info(f"Interest rates saved to {filepath}")
        return filepath

