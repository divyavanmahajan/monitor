# Implementation Plan: Complete Removal of InfluxDB Integration

## Goals
Remove all remaining code, documentation, and historical records related to InfluxDB.

## Steps
1. **Code Cleanup**:
   - Done: Removed `--influx` and `--importcsv` from `energymeter.py`.
   - Done: Verified `openweathermap.py` and `evohome.py` are clean.
2. **Documentation Cleanup**:
   - Done: Removed InfluxDB sections from `PollWeather.md`.
   - Done: Purged all InfluxDB mentions from `Architecture.md`.
   - Done: Verified `UserGuide.md`, `PollRooms.md`, and `PollEnergyMeter.md` are clean.
3. **Project Purge**:
   - Done: Deleted `docs/issues/001`, `docs/issues/004`, and `docs/issues/9`.
4. **Verification**:
   - Done: Ran `uv run pytest`.
   - Done: Verified no "influx" mentions remain using `ripgrep`.
