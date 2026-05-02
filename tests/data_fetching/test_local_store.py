import pandas as pd

from risk_factors.data_fetching.local_store import (
    load_local_levels,
    load_local_metadata,
    save_local_levels,
)


def test_local_store_round_trip(tmp_path):
    levels = pd.DataFrame(
        {"date": ["2025-01-02", "2025-01-01"], "factor": [2.0, 1.0]}
    )
    levels_path = tmp_path / "levels.parquet"
    metadata_path = tmp_path / "metadata.json"

    saved_path = save_local_levels(levels, levels_path, metadata_path=metadata_path)
    loaded = load_local_levels(saved_path)
    metadata = load_local_metadata(metadata_path)

    assert loaded.index.tolist() == [
        pd.Timestamp("2025-01-01"),
        pd.Timestamp("2025-01-02"),
    ]
    assert loaded["factor"].tolist() == [1.0, 2.0]
    assert metadata["rows"] == 2
    assert metadata["columns"] == ["factor"]
