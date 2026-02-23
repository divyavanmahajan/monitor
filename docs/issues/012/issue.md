# User Story: Complete Removal of InfluxDB Integration

**As a user**, I want all traces of InfluxDB removed from the codebase and documentation, so that the monitoring suite is clean and focused solely on SQLite and CSV storage.

## Acceptance Criteria
- [x] Remove InfluxDB arguments and logic from `energymeter.py`.
- [x] Remove InfluxDB arguments and logic from `openweathermap.py` (already clean).
- [x] Update `Architecture.md` to remove all InfluxDB sections, diagrams, and volume estimates.
- [x] Update `PollWeather.md` to remove InfluxDB configuration and examples.
- [x] Remove historical InfluxDB-related issues from `docs/issues/` (001, 004, 9).
- [x] Ensure `pyproject.toml` contains no InfluxDB dependencies.
- [x] Verify all polling scripts run successfully without InfluxDB errors.
- [x] Verify tests pass.
