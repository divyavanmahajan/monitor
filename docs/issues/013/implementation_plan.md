# Implementation Plan - Modular Monitor Refactor

Refactor the home automation monitor into a modular architecture with distinct blocks for data retrieval (Sources), storage (Sinks), and polling management (Controller).

## User Review Required

> [!IMPORTANT]
> The polling scripts will now be integrated into a single async loop. Individual script entry points (`mesura-energy`, `mesura-weather`, `mesura-evohome`) will be maintained as thin wrappers for backward compatibility, but the preferred way will be a single command.

> [!NOTE]
> All storage will now target a single SQLite database (`monitor.db`) in the specified data folder, with tables renamed for clarity: `energy`, `weather`, and `evohome`.

## Proposed Changes

### Core Infrastructure (`src/dvm_mesura/core/`)

#### [NEW] [base.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/core/base.py)
Define `BaseMonitor` and `BaseBackend` abstract base classes.
- `BaseMonitor`: `fetch_data()`, `process_data()`.
- `BaseBackend`: `write(data, source_name)`.

#### [NEW] [controller.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/core/controller.py)
Implement `PollingController` to handle per-monitor loops and `MasterController` for concurrent execution using `asyncio`.

#### [NEW] [helpers.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/core/helpers.py)
Consolidate common logic:
- `parse_interval`
- `format_time_display`
- `flatten_dict` (generic version of `flatten_data`)

---

### Storage Backends (`src/dvm_mesura/backends/`)

#### [NEW] [sqlite.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/backends/sqlite.py)
Implement `SQLiteBackend` with automatic schema evolution.

#### [NEW] [csv.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/backends/csv.py)
Implement `CSVBackend` to manage separate files per monitor.

---

### Monitors (`src/dvm_mesura/monitors/`)

#### [NEW] [energy.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/monitors/energy.py)
Energy meter specific implementation.

#### [NEW] [weather.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/monitors/weather.py)
OpenWeatherMap specific implementation.

#### [NEW] [evohome.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/monitors/evohome.py)
Honeywell Evohome specific implementation.

---

### Entry Points and Main Logic

#### [MODIFY] [main.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/main.py)
Update to be the main entry point that configures and runs the `MasterController`.

#### [MODIFY] [energymeter.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/energymeter.py)
#### [MODIFY] [openweathermap.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/openweathermap.py)
#### [MODIFY] [evohome.py](file:///Users/divya/Documents/projects/homeautomation/monitor/src/dvm_mesura/evohome.py)
Convert to thin wrappers that use the new modular classes.

## Verification Plan

### Automated Tests
- Run existing tests to ensure no regressions:
  ```bash
  uv run pytest
  ```
- Add unit tests for `BaseMonitor`, `BaseBackend`, and the `Controller` (verified 13 tests passing).
- Verify schema evolution in `SQLiteBackend` specifically.
- Support `h` (hours) in interval strings.

### Manual Verification
- Run `uv run mesura-all` (new command).
- Check `data/` directory:
  - Verify `monitor.db` exists and contains tables for each monitor.
  - Verify `energy.csv`, `weather.csv`, and `rooms.csv` are updated.
- Verify polling intervals (e.g., set short intervals for testing).
