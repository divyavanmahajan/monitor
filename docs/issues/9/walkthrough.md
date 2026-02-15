# Walkthrough - Removing InfluxDB Integration

I have successfully removed the InfluxDB integration from the home automation monitoring suite, transitioning the system to use local SQLite and CSV storage for all data.

## Changes Made

### 1. Unified Monitor Script (`monitor_all.sh`)
- Removed InfluxDB startup logic and health checks.
- Deleted the InfluxDB tmux pane in interactive mode.
- Updated the tmux layout to use 3 panes: **Energy**, **Rooms**, and **Weather**.
- Removed InfluxDB-related color coding and prefixes.

### 2. Python Polling Scripts
Modified `poll_evohome_standalone.py`, `poll_energymeter.py`, and `poll_openweathermap.py` to:
- Remove `influxdb_client_3` imports and dependencies.
- Delete `--influx` and `--importcsv` command-line arguments.
- Remove InfluxDB client initialization and write logic.

### 3. Cleanup of Obsolete Files
Deleted the following InfluxDB-specific helper scripts:
- `scripts/start_influx.sh`
- `scripts/influx_query.sh`
- `scripts/check_influxdb_schema.py`
- `scripts/test_line_protocol.py`
- `scripts/test_influxdb_connection.py`

## Verification Results

### Unified Monitor Output
I verified that `monitor_all.sh` now correctly manages three polling processes without attempting to start InfluxDB.

### Data Persistence
Polling scripts were verified to record data correctly into SQLite databases and CSV files.

## Documentation Update
The `README.md` has been updated to remove InfluxDB-specific sections and reflect the new system architecture.
## CLI Standardization (Issue #9)
I have standardized the command-line interface for `poll_evohome_standalone.py` to match `poll_energymeter.py` and `poll_openweathermap.py`.

### Changes Made:
- Added `argparse` to handle command-line options.
- Implemented `-i`/`--interval` with support for 's' and 'm' suffixes.
- Added `-o`/`--output` to specify CSV output file path (SQLite DB follows the same name).
- Added `--overwrite` and `--noshow` flags.
- Implemented a premium table display with `tabulate` (if available).
- Integrated keyboard interaction: press **'L'** during execution to show the table header.

### Verification Results:
- Verified `--help` output for correct argument definitions.
- Tested `-i 10s` and confirmed data is polled every 10 seconds.
- Verified that data is written to both the specified CSV and the corresponding SQLite database.
- Confirmed `--noshow` suppresses the table output as expected.
