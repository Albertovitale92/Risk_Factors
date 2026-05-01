"""Local storage for historical risk-factor levels."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from risk_factors.utils import get_logger, read_json, write_json


DEFAULT_DATA_DIR = Path("data") / "raw"
DEFAULT_LEVELS_PATH = DEFAULT_DATA_DIR / "risk_factors_levels.parquet"
DEFAULT_METADATA_PATH = DEFAULT_DATA_DIR / "risk_factors_metadata.json"

logger = get_logger(__name__)


def _normalize_levels(levels: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(levels, pd.DataFrame):
        raise TypeError("levels must be a pandas DataFrame")
    if levels.empty:
        return levels.copy()

    normalized = levels.copy()
    if "date" in normalized.columns:
        normalized["date"] = pd.to_datetime(normalized["date"])
        normalized = normalized.set_index("date")
    else:
        normalized.index = pd.to_datetime(normalized.index)

    normalized = normalized.sort_index()
    normalized = normalized[~normalized.index.duplicated(keep="last")]
    normalized.index.name = "date"
    return normalized


def load_local_levels(path: str | Path = DEFAULT_LEVELS_PATH) -> pd.DataFrame:
    """Load locally stored risk-factor levels from Parquet."""
    levels_path = Path(path)
    if not levels_path.exists():
        logger.info("Local risk-factor levels file not found: %s", levels_path)
        return pd.DataFrame()

    levels = pd.read_parquet(levels_path)
    return _normalize_levels(levels)


def save_local_levels(
    levels: pd.DataFrame,
    path: str | Path = DEFAULT_LEVELS_PATH,
    *,
    metadata_path: str | Path = DEFAULT_METADATA_PATH,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """Save risk-factor levels to local Parquet storage."""
    levels_path = Path(path)
    levels_path.parent.mkdir(parents=True, exist_ok=True)

    normalized = _normalize_levels(levels)
    normalized.to_parquet(levels_path)

    metadata_payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "path": str(levels_path),
        "rows": len(normalized),
        "columns": list(normalized.columns),
        "start_date": normalized.index.min().strftime("%Y-%m-%d") if not normalized.empty else None,
        "end_date": normalized.index.max().strftime("%Y-%m-%d") if not normalized.empty else None,
    }
    if metadata:
        metadata_payload.update(metadata)
    write_json(metadata_payload, metadata_path, indent=2)

    logger.info("Saved local risk-factor levels to %s", levels_path)
    return levels_path


def load_local_metadata(path: str | Path = DEFAULT_METADATA_PATH) -> dict[str, Any]:
    """Load metadata for the local risk-factor levels store."""
    metadata_path = Path(path)
    if not metadata_path.exists():
        return {}
    return read_json(metadata_path)


def update_local_levels(
    *,
    years: int = 10,
    start_date=None,
    end_date=None,
    path: str | Path = DEFAULT_LEVELS_PATH,
    metadata_path: str | Path = DEFAULT_METADATA_PATH,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Fetch and merge historical risk-factor levels into the local store."""
    existing = load_local_levels(path)
    target_end = pd.Timestamp(end_date or datetime.now().date())

    if not force_refresh and not existing.empty and existing.index.max() >= target_end:
        logger.info("Local risk-factor levels are already current through %s", target_end.date())
        return existing

    from risk_factors.data_fetching.historical_fetcher import HistoricalDataFetcher

    logger.info("Fetching historical risk-factor levels for local store")
    data_dir = Path(path).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    fetcher = HistoricalDataFetcher(
        data_dir=str(data_dir),
        years=years,
        start_date=start_date,
        end_date=end_date,
    )
    fetched = _normalize_levels(fetcher.fetch_historical_data())

    if existing.empty:
        updated = fetched
    else:
        updated = pd.concat([existing, fetched]).sort_index()
        updated = updated[~updated.index.duplicated(keep="last")]

    save_local_levels(
        updated,
        path=path,
        metadata_path=metadata_path,
        metadata={
            "years": years,
            "requested_start_date": start_date,
            "requested_end_date": end_date,
            "force_refresh": force_refresh,
        },
    )
    return updated
