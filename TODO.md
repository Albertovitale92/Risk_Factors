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
