# Poll Energy Meter Script Documentation

The `poll_energymeter.py` script continuously polls the P1 Energy Meter API and logs energy data to a CSV file and a SQLite database.

## Overview

The script fetches energy meter data from a P1 Energy Meter device at regular intervals and stores it in multiple formats. It automatically flattens nested JSON data and provides a real-time table display in the terminal.

## Location

The script is located at: `scripts/poll_energymeter.py`

## Prerequisites

### Required Python Packages

- `requests`: For HTTP requests to the P1 Energy Meter API
- `aiohttp`: For asynchronous communication (if applicable)
- `python-dotenv`: For loading environment variables
- `tabulate`: For table formatting (optional)

## Usage

### Basic Usage

```bash
python3 scripts/poll_energymeter.py -o data/energy.csv
```

This will:
- Poll the API every 1 minute (default)
- Write data to `data/energy.csv` (CSV) and `data/energy.db` (SQLite)
- Display data on screen in a table
- Append to files if they already exist

### Command-Line Options

- **`-i`, `--interval`** (default: `1m`): Polling interval
  - Supports 's' (seconds) and 'm' (minutes) suffixes.
  - Examples: `30s`, `1m`, `5m`, `10m`.

- **`-o`, `--output`** (required): Output CSV file path.
  - The SQLite database will use the same base name (e.g., `-o data/energy.csv` creates `data/energy.db`).

- **`--overwrite`** (flag): Overwrite existing files.
  - Replaces existing files instead of appending.

- **`--noshow`** (flag): Do not display data on screen.
  - Only logs to files (useful for background tasks).

### Examples

```bash
# Poll every 5 minutes
python3 scripts/poll_energymeter.py -i 5m -o data/energy.csv

# Poll every 30 seconds, overwrite existing data
python3 scripts/poll_energymeter.py -i 30s -o data/energy.csv --overwrite

# Poll every hour, no screen display
python3 scripts/poll_energymeter.py -i 60m -o data/energy.csv --noshow
```

## Data Storage

### CSV Output
Flattened JSON data with a UTC timestamp. Nested fields use underscore notation (e.g., `data_power`).

### SQLite Database
A relational database with a `readings` table. The schema evolves automatically to include new fields from the energy meter API.

#### Inspecting SQLite Data
```bash
sqlite3 data/energy.db "SELECT * FROM readings ORDER BY timestamp DESC LIMIT 5"
```

## Screen Display

Displays key metrics in a live table:
- **Time**: Local time of reading.
- **Tariff**: Active tariff.
- **Gas (m³)**: Total gas consumption.
- **Import T1/T2 (kWh)**: Cumulative energy imported.
- **Total (kWh)**: Combined import.

### Interactive Features
- **Press 'L'**: Re-display the table header.
- **Press Ctrl+C**: Stop the script gracefully.

## Error Handling
- Retries on network timeouts or API errors.
- Logs warnings if a data source is temporarily unavailable.

