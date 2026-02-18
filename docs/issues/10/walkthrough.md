# Walkthrough - Timezone Normalization to UTC/Z

I have standardized the timezone handling across all three polling scripts to ensure consistency in data storage and display.

## Changes Made

### 1. `scripts/poll_energymeter.py`
- Added `timezone` import from `datetime`.
- Updated `format_time_display()` to append `Z` to the formatted display string (e.g., `18/02 18:52Z`).
- Updated the main poll loop to record timestamps in UTC with the `Z` suffix: `YYYY-MM-DDTHH:MM:SSZ`.
- Updated on-screen "Updated:" status line to use UTC and `Z`.

### 2. `scripts/poll_evohome_standalone.py`
- Updated `format_time_display()` to include `Z` in the formatted output.
- Changed recorded `timestamp` from `datetime.now(timezone.utc).isoformat()` to `strftime('%Y-%m-%dT%H:%M:%SZ')` for explicit `Z` suffix.
- Updated all on-screen display timestamps to show UTC time with the `Z` suffix.

### 3. `scripts/poll_openweathermap.py`
- Added `timezone` import from `datetime`.
- Updated `flatten_weather_data()` to convert Unix timestamps for `sunrise` and `sunset` into UTC ISO strings with the `Z` suffix.
- Updated `format_time_display()` to treat input Unix timestamps as UTC and display with a `Z` suffix.
- Updated recorded `timestamp` to use UTC with `Z`.
- Updated on-screen status lines to show timestamps in UTC and `Z`.

## Verification Results
- All scripts now generate a `timestamp` field ending in `Z`.
- Displayed times now look like `18/02 18:52Z`.
- Status lines look like `Updated: 2026-02-18 18:52:47Z`.
