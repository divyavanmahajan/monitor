# Implementation Plan - Timezone Normalization

## Proposed Changes

### 1. `scripts/poll_energymeter.py`
- Update `from datetime import datetime` to `from datetime import datetime, timezone`.
- Update data collection loop to use `datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')` for the `timestamp` field.
- Update `format_time_display` to include `Z` in the output format: `dt.strftime("%d/%m %H:%MZ")`.
- Update the "Updated:" display timestamp to use UTC and `Z`.

### 2. `scripts/poll_evohome_standalone.py`
- Update data collection loop to use `now.strftime('%Y-%m-%dT%H:%M:%SZ')` for the `timestamp` field (where `now` is already UTC-aware).
- Update `format_time_display` to include `Z` in the output format: `dt.strftime("%d/%m %H:%M:%SZ")`.
- Update the "Updated:" display timestamp to use UTC and `Z`.

### 3. `scripts/poll_openweathermap.py`
- Update `from datetime import datetime` to `from datetime import datetime, timezone`.
- Update `flatten_weather_data` to:
    - Use `datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')` for `sunrise` and `sunset`.
- Update data collection loop to use `datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')` for the `timestamp` field.
- Update `format_time_display` to convert Unix timestamps to UTC before formatting: `datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%d/%m %H:%MZ")`.
- Update the "Updated:" display timestamp to use UTC and `Z`.

## Verification Plan
1. Run each script in a terminal (mocking or using actual API if possible) and verify:
    - The terminal display shows `Z` for all times.
    - The "Updated" time shows `Z`.
    - Check the resulting CSV or SQLite database to ensure the stored `timestamp` ends in `Z`.
