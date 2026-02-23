# Poll Rooms Script Documentation

The `poll_evohome_standalone.py` script polls room temperature data from the Honeywell Evohome (TCC) API and logs it to a CSV file and a SQLite database.

## Overview

This script fetches current temperature and setpoint data for all zones in your Honeywell Evohome system. It handles authentication automatically using the credentials provided in your `.env` file.

## Location

The script is located at: `scripts/poll_evohome_standalone.py`

## Prerequisites

### Required Configuration
Add your Evohome credentials to the `.env` file:
```ini
EVOHOME_EMAIL=your_email@example.com
EVOHOME_PASSWORD=your_password_here
```

### Required Python Packages
- `aiohttp`: For asynchronous API requests
- `python-dotenv`: For loading environment variables
- `tabulate`: For real-time terminal display

## Usage

### Basic Usage
```bash
python3 scripts/poll_evohome_standalone.py -o data/rooms.csv
```

### Command-Line Options

- **`-i`, `--interval`** (default: `1m`): Polling interval
  - Supports 's' (seconds) and 'm' (minutes) suffixes.
  - Example: `1m`, `5m`, `10m`.

- **`-o`, `--output`** (required): Output CSV file path.
  - The SQLite database uses the same base name (`data/rooms.db`).

- **`--overwrite`**: Overwrite existing files.

- **`--noshow`**: Disable the on-screen table display.

## Data Storage

### CSV Output
Logs zone names, current temperatures, and setpoints with a UTC timestamp.

### SQLite Database
Stores data in the `temperatures` table for long-term analysis.

#### Example Query
```bash
sqlite3 data/rooms.db "SELECT zone_name, temp, setpoint FROM temperatures ORDER BY timestamp DESC LIMIT 10"
```

## Screen Display

The script displays a live table of all zones:
- **Zone**: Name of the heating zone.
- **Temp**: Current temperature.
- **Setpoint**: Target temperature.
- **Status**: Visual indicator of heating status.

### Interactive Features
- **Press 'L'**: Re-display the table header.
- **Press Ctrl+C**: Stop the script gracefully.
