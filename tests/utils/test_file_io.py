from risk_factors.utils import read_csv, read_json, read_parquet, write_csv, write_json, write_parquet

import pandas as pd


def test_csv_json_and_parquet_round_trips(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})

    csv_path = tmp_path / "nested" / "data.csv"
    json_path = tmp_path / "nested" / "data.json"
    parquet_path = tmp_path / "nested" / "data.parquet"

    write_csv(df, csv_path, index=False)
    write_json({"ok": True}, json_path)
    write_parquet(df, parquet_path)

    assert read_csv(csv_path).equals(df)
    assert read_json(json_path) == {"ok": True}
    assert read_parquet(parquet_path).equals(df)
