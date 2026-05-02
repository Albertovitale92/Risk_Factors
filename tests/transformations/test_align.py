import pandas as pd

from risk_factors.transformations import align_time_series


def test_align_time_series_uses_common_index():
    left = pd.Series([1.0, 2.0], index=pd.to_datetime(["2025-01-01", "2025-01-02"]))
    right = pd.DataFrame(
        {"value": [10.0, 20.0]},
        index=pd.to_datetime(["2025-01-02", "2025-01-03"]),
    )

    aligned_left, aligned_right = align_time_series(left, right)

    assert aligned_left.index.tolist() == [pd.Timestamp("2025-01-02")]
    assert aligned_right.index.tolist() == [pd.Timestamp("2025-01-02")]
