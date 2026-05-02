# TODO

## Regime Detection Module

- Add a dedicated module for regime detection, likely `risk_factors/regimes/` or `risk_factors/transformations/regimes.py`.
- The module can reuse existing transformation helpers such as returns, rolling volatility, rolling correlations, and correlation matrices.
- Consider adding new functions for:
  - volatility regime classification
  - correlation regime shifts
  - threshold-based regime labels
  - clustering-based regimes
  - change-point detection
- Keep the API explicit about the input assumptions: risk-factor shocks should be constructed before regime detection using the appropriate return convention.

## Risk Metrics Modules

Implement analytics that operate on returns, exposures, or curves.

### `risk_factors/risk_metrics/beta.py`

- `compute_beta(asset_returns, benchmark_returns)`
- `compute_multi_beta(returns_df, benchmark_returns)`

### `risk_factors/risk_metrics/duration.py`

- `macaulay_duration(cashflows, yields)`
- `modified_duration(cashflows, yields)`
- `key_rate_durations(curve, shocks)`
- Upgrade `key_rate_durations` from the current curve-shock placeholder to a true price-based key-rate duration once curve building and pricing logic exist. Target API:

```python
key_rate_durations(
    instrument_or_portfolio,
    curve,
    pricing_function,
    shock_size=0.0001,
)
```

The upgraded function should compute:

```text
KRD_i = - (P_shocked_i - P_base) / (P_base * shock_i)
```

### `risk_factors/risk_metrics/fx_exposure.py`

- `compute_fx_exposure(positions, fx_rates)`
- `portfolio_fx_sensitivity(positions, fx_returns)`

### `risk_factors/risk_metrics/factor_model.py`

- `ols_factor_exposures(returns, factors)`
- `pca_factors(returns)`
- `factor_risk_contribution(returns, exposures, cov_matrix)`

## Curves Builder Modules

Implement the curve-building stack for market instruments, interpolation, and bootstrapping.

### `risk_factors/curves/curve_builder.py`

Build yield curves from raw market instruments. Support:

- deposits
- futures
- swaps
- OIS
- government bonds

### `risk_factors/curves/interpolation.py`

- linear interpolation
- log-linear interpolation
- cubic spline interpolation
- monotone convex interpolation, optional

### `risk_factors/curves/bootstrapping.py`

- bootstrap discount factors
- bootstrap forward rates
- bootstrap zero curves

## Review Implemented Modules

- Review and harden the implemented transformations, utility helpers, public API, and local data store.
- Check edge cases, naming consistency, docstrings, and API ergonomics before treating them as stable.
- Expand test coverage around real market-data quirks after the core implementation is reviewed.
