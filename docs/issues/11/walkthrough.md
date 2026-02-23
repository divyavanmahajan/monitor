# Walkthrough: Implementing Mocked Tests

## Summary of Changes
Implemented a test suite using `pytest`, `pytest-mock`, and `responses` to verify the core logic of the monitoring scripts without requiring real hardware or internet connection.

## Key Components
1. **API Mocking**: Used `responses` to intercept HTTP calls to the Energy Meter and OpenWeatherMap APIs.
2. **Database Mocking**: Used `pytest`'s `tmp_path` fixture to create isolated SQLite databases for each test run.
3. **Schema Evolution Testing**: Verified that the dynamic SQLite schema generation works as expected.

## How to Run
```bash
pytest
```
