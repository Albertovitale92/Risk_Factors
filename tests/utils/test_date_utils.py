import pandas as pd

from risk_factors.utils import (
    get_business_days,
    get_month_end,
    get_quarter_end,
    shift_business_days,
    to_datetime,
)


def test_date_helpers():
    assert to_datetime("2025-04-15") == pd.Timestamp("2025-04-15")
    assert get_business_days("2025-04-18", "2025-04-21").tolist() == [
        pd.Timestamp("2025-04-18"),
        pd.Timestamp("2025-04-21"),
    ]
    assert shift_business_days("2025-04-18", 1) == pd.Timestamp("2025-04-21")
    assert get_month_end("2025-04-15") == pd.Timestamp("2025-04-30")
    assert get_quarter_end("2025-04-15") == pd.Timestamp("2025-06-30")
