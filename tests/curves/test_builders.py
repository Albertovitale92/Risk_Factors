import math

import pandas as pd
import pytest

from risk_factors.curves import bootstrap_ecb_ois_zero_curve, tenor_to_years


def test_tenor_to_years_supports_standard_ois_buckets():
    assert tenor_to_years("1M") == pytest.approx(1 / 12)
    assert tenor_to_years("12M") == pytest.approx(1.0)
    assert tenor_to_years("10Y") == pytest.approx(10.0)


def test_direct_mode_converts_each_bucket_rate_to_zero_curve():
    curve = pd.DataFrame(
        {
            "tenor": ["1M", "12M", "2Y"],
            "value": [3.0, 3.2, 3.5],
        }
    )

    result = bootstrap_ecb_ois_zero_curve(curve, mode="direct")

    expected_discount_factor = 1 / (1 + 0.035 * 2.0)
    assert list(result.columns) == [
        "tenor",
        "maturity_years",
        "par_rate",
        "discount_factor",
        "zero_rate_continuous",
        "zero_rate_annual",
    ]
    assert result.loc[result["tenor"] == "2Y", "par_rate"].iloc[0] == pytest.approx(0.035)
    assert result.loc[result["tenor"] == "2Y", "discount_factor"].iloc[0] == pytest.approx(
        expected_discount_factor
    )


def test_par_mode_bootstraps_long_end_after_simple_short_end():
    curve = pd.DataFrame(
        {
            "tenor": ["12M", "2Y"],
            "value": [3.0, 4.0],
        }
    )

    result = bootstrap_ecb_ois_zero_curve(curve, mode="par", rate_unit="percent")

    df_1y = 1 / 1.03
    df_2y = (1 - 0.04 * df_1y) / 1.04
    row_2y = result[result["tenor"] == "2Y"].iloc[0]
    assert row_2y["discount_factor"] == pytest.approx(df_2y)
    assert row_2y["zero_rate_continuous"] == pytest.approx(-math.log(df_2y) / 2)


def test_par_mode_interpolates_missing_fixed_payment_discount_factors():
    curve = pd.DataFrame(
        {
            "tenor": ["12M", "2Y", "3Y", "5Y"],
            "value": [3.0, 3.2, 3.4, 3.8],
        }
    )

    result = bootstrap_ecb_ois_zero_curve(curve, mode="par")

    assert result["discount_factor"].notna().all()
    assert result.loc[result["tenor"] == "5Y", "discount_factor"].iloc[0] < result.loc[
        result["tenor"] == "3Y", "discount_factor"
    ].iloc[0]


def test_invalid_mode_raises_value_error():
    with pytest.raises(ValueError):
        bootstrap_ecb_ois_zero_curve({"1Y": 0.03}, mode="unknown")
