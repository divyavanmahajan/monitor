# Task: Implement Mocked Tests for External APIs and Databases

Implement a test suite that mocks external API calls and uses mock database files for the `monitor-suite` project.

## Requirements
- Mock external API calls (Energy Meter, OpenWeatherMap, Evohome).
- Use temporary mock database files for SQLite interactions.
- Ensure tests are repeatable and do not depend on external services or real local databases.
- Integrate with `pytest`.

## Proposed Changes
1. Add testing dependencies to `pyproject.toml`.
2. Create a `tests/` directory.
3. Implement mocks for:
    - `requests.get` (or use `responses` library).
    - `sqlite3.connect`.
4. Add unit tests for `energymeter.py` and `openweathermap.py`.
