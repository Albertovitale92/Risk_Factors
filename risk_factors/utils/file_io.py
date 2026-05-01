"""File input/output helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PathLike = str | Path


def ensure_folder_exists(path: PathLike) -> Path:
    """Ensure a folder exists and return it as a Path."""
    folder = Path(path)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _ensure_parent_folder(path: PathLike) -> Path:
    file_path = Path(path)
    if file_path.parent != Path("."):
        file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def read_csv(path: PathLike, **kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(Path(path), **kwargs)


def write_csv(df: pd.DataFrame, path: PathLike, **kwargs) -> None:
    """Write a DataFrame to CSV."""
    file_path = _ensure_parent_folder(path)
    df.to_csv(file_path, **kwargs)


def read_json(path: PathLike) -> Any:
    """Read a JSON file into a Python object."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(obj: Any, path: PathLike, **kwargs) -> None:
    """Write a Python object to JSON."""
    file_path = _ensure_parent_folder(path)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(obj, file, **kwargs)


def read_parquet(path: PathLike, **kwargs) -> pd.DataFrame:
    """Read a Parquet file into a DataFrame."""
    return pd.read_parquet(Path(path), **kwargs)


def write_parquet(df: pd.DataFrame, path: PathLike, **kwargs) -> None:
    """Write a DataFrame to Parquet."""
    file_path = _ensure_parent_folder(path)
    df.to_parquet(file_path, **kwargs)
