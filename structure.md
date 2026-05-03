# Structure

```text
Risk_Factors/
├── risk_factors/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── data_fetching/
│   │   ├── __init__.py
│   │   └── providers.py
│   ├── transformations/
│   │   ├── __init__.py
│   │   └── operations.py
│   ├── curves/
│   │   ├── __init__.py
│   │   └── builders.py
│   ├── risk_analytics/
│   │   ├── __init__.py
│   │   └── calculations.py
│   ├── risk_metrics/
│   │   ├── __init__.py
│   │   ├── expected_shortfall.py
│   │   └── var.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── api/
│       ├── __init__.py
│       └── facade.py
└── tests/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── test_settings.py
    ├── data_fetching/
    │   ├── __init__.py
    │   └── test_providers.py
    ├── transformations/
    │   ├── __init__.py
    │   └── test_operations.py
    ├── curves/
    │   ├── __init__.py
    │   └── test_builders.py
    ├── risk_analytics/
    │   ├── __init__.py
    │   └── test_calculations.py
    ├── risk_metrics/
    │   ├── __init__.py
    │   ├── test_expected_shortfall.py
    │   └── test_var.py
    ├── utils/
    │   ├── __init__.py
    │   └── test_helpers.py
    └── api/
        ├── __init__.py
        └── test_facade.py
```
