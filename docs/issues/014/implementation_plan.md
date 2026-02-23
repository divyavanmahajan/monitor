# Implementation Plan - CLI Enhancements (Setup & Separate DBs)

Add interactive configuration and flexible database layout options to the monitoring suite.

## Proposed Changes

### Configuration Setup (`src/dvm_mesura/setup.py`)
- **[NEW] [setup.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/setup.py)**: Implement an interactive setup wizard.
  - Read existing `.env` using `dotenv`.
  - Prompt for settings:
    - Energy: `ENERGY_API_URL`
    - Weather: `OPENWEATHER_API_KEY`, Latitude, Longitude
    - Evohome: `EVOHOME_USERNAME`, `EVOHOME_PASSWORD`
  - Use existing values as defaults.
  - Write back to `.env`.

### Main Entry Point (`src/dvm_mesura/main.py`)
- **[MODIFY] [main.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/main.py)**:
  - Add `--separate` flag: If enabled, pass `{name}.db` to `SQLiteBackend` during controller initialization rather than a shared `monitor.db`.
  - Add `--setup` flag: If enabled, call the setup wizard and exit.

## Verification Plan

### Manual Verification
- Run `uv run mesura-all --setup` and verify `.env` is updated correctly.
- Run `uv run mesura-all --separate` and verify `energy.db`, `weather.db`, and `evohome.db` are created and contain data.
- Verify that standard `uv run mesura-all` still uses a shared `monitor.db`.
