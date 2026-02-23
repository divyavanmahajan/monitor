# Walkthrough: Implementing Mocked Tests

## Summary of Changes
Implemented a test suite using `pytest`, `pytest-mock`, and `responses` to verify the core logic of the monitoring scripts without requiring real hardware or internet connection.

## Key Components
1. **API Mocking**: Used `responses` to intercept HTTP calls to the Energy Meter and OpenWeatherMap APIs.
2. **Database Mocking**: Used `pytest`'s `tmp_path` fixture to create isolated SQLite databases for each test run.
3. **Schema Evolution Testing**: Verified that the dynamic SQLite schema generation works as expected.

## How to Run
Tests are executed using `pytest`. You must set the `PYTHONPATH` to include the `src` directory so the `monitor` package can be discovered.

```bash
PYTHONPATH=src ./.venv/bin/python3 -m pytest tests/
```

### Results
All 5 tests passed successfully, covering:
- API mocking for Energy Meter and OpenWeatherMap.
- SQLite persistence with automatic schema evolution.
- Data flattening logic.
