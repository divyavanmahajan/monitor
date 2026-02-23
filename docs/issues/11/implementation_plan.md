# Implementation Plan: Mocked Tests

## Proposed Changes

### 1. Dependency Management
Add the following development dependencies:
- `pytest`
- `pytest-mock`
- `responses`

### 2. Test Infrastructure
- Create `tests/conftest.py` for shared fixtures.
- Define a fixture for a temporary SQLite database.

### 3. Energy Meter Tests (`tests/test_energymeter.py`)
- Mock `requests.get` to return a sample JSON energy reading.
- Verify `fetch_energy_data` correctly handles the response.
- Use a temporary file for `write_to_sqlite` and verify the data is correctly inserted.

### 4. OpenWeatherMap Tests (`tests/test_openweathermap.py`)
- Mock the OpenWeatherMap API call.
- Verify `flatten_weather_data` correctly processes various API responses (including missing fields).
- Verify `write_to_sqlite` evolves the schema correctly in a mock environment.

## Verification Plan

### Automated Tests
Run `pytest` and ensure all tests pass.
```bash
pytest
```

### Manual Verification
Inspect the temporary `.db` files created during tests (if they aren't auto-deleted) to ensure structure is correct.
