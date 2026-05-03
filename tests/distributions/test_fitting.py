import pandas as pd
import pytest

from risk_factors.distributions import (
    fit_distribution,
    fit_normaldist_distribution,
    fit_student_t_distribution,
)


def test_fit_normaldist_distribution_from_numeric_series():
    returns = pd.Series([-0.02, -0.01, 0.0, 0.01, 0.02], name="asset_returns")

    fitted = fit_normaldist_distribution(returns)

    assert fitted.distribution == "normal"
    assert fitted.mean == pytest.approx(0.0)
    assert fitted.volatility == pytest.approx(returns.std(ddof=1))
    assert fitted.sample_size == 5
    assert fitted.source_name == "asset_returns"
    assert fitted.parameters == {
        "loc": pytest.approx(0.0),
        "scale": pytest.approx(returns.std(ddof=1)),
    }


def test_fitted_distribution_quantile_cdf_and_pdf():
    fitted = fit_normaldist_distribution(pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0]))

    assert fitted.quantile(0.5) == pytest.approx(0.0)
    assert fitted.cdf(0.0) == pytest.approx(0.5)
    assert fitted.pdf(0.0) > 0


def test_fitted_distribution_simulate_is_reproducible():
    fitted = fit_normaldist_distribution(pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0]))

    scenarios = fitted.simulate(3, seed=7, name="simulated_returns")

    assert len(scenarios) == 3
    assert scenarios.name == "simulated_returns"
    assert scenarios.equals(fitted.simulate(3, seed=7, name="simulated_returns"))


def test_fit_normaldist_distribution_handles_pnl_series():
    pnl = pd.Series([-100.0, -50.0, 25.0, 50.0])

    fitted = fit_normaldist_distribution(pnl, name="pnl")

    assert fitted.quantile(0.05) < 0


def test_fit_distribution_dispatches_supported_distribution():
    fitted = fit_distribution(pd.Series([-1.0, 0.0, 1.0]), distribution="normal")

    assert fitted.distribution == "normal"


def test_fit_student_t_distribution_from_fat_tailed_series():
    returns = pd.Series([-8.0, -2.0, -1.0, 0.0, 1.0, 2.0, 8.0], name="returns")

    fitted = fit_student_t_distribution(returns)

    assert fitted.distribution == "student_t"
    assert fitted.mean == pytest.approx(0.0)
    assert fitted.volatility == pytest.approx(returns.std(ddof=1))
    assert fitted.df is not None
    assert fitted.df > 4
    assert fitted.parameters["df"] == pytest.approx(fitted.df)
    assert fitted.parameters["loc"] == pytest.approx(fitted.loc)
    assert fitted.parameters["scale"] == pytest.approx(fitted.scale)


def test_fit_student_t_distribution_quantile_cdf_pdf_and_simulation():
    fitted = fit_student_t_distribution(pd.Series([-8.0, -2.0, -1.0, 0.0, 1.0, 2.0, 8.0]))

    assert fitted.quantile(0.5) == pytest.approx(0.0, abs=1e-3)
    assert fitted.cdf(0.0) == pytest.approx(0.5, abs=1e-3)
    assert fitted.pdf(0.0) > 0
    assert len(fitted.simulate(5, seed=11)) == 5


def test_fit_distribution_dispatches_student_t():
    fitted = fit_distribution(pd.Series([-8.0, -1.0, 0.0, 1.0, 8.0]), distribution="student_t")

    assert fitted.distribution == "student_t"


def test_fit_distribution_rejects_unsupported_distribution():
    with pytest.raises(ValueError):
        fit_distribution(pd.Series([-1.0, 0.0, 1.0]), distribution="skew_normal")


def test_fit_normaldist_distribution_rejects_non_series():
    with pytest.raises(TypeError):
        fit_normaldist_distribution([-1.0, 0.0, 1.0])


def test_fitted_distribution_rejects_invalid_simulation_count():
    fitted = fit_normaldist_distribution(pd.Series([1.0, 2.0, 3.0]))

    with pytest.raises(ValueError):
        fitted.simulate(0)
