# Task: Timezone Normalization to UTC/Z

Standardize time display and storage across all polling scripts to consistently use UTC with the `Z` suffix.

## Requirements
- All `poll_*.py` scripts must store timestamps in ISO 8601 format with the `Z` suffix (UTC).
- All on-screen displays (terminal output) must show times in UTC with a `Z` suffix.
- Consistency across `poll_energymeter.py`, `poll_evohome_standalone.py`, and `poll_openweathermap.py`.

## Affected Files
- `scripts/poll_energymeter.py`
- `scripts/poll_evohome_standalone.py`
- `scripts/poll_openweathermap.py`
