# User Guide - Home Automation Monitoring Suite

This guide covers everything you need to know about using and personalizing the home automation monitoring suite.

## Getting Started

### 1. Installation

Standard Python dependencies are required:
```bash
pip install requests python-dotenv tabulate aiohttp
```

### 2. Configuration

Create a `.env` file in the root directory:
```ini
# Honeywell Evohome
EVOHOME_EMAIL=your_email@example.com
EVOHOME_PASSWORD=your_password_here

# OpenWeatherMap
OPENWEATHER_API_KEY=your_api_key_here
```

## Monitoring Details

The suite consists of three main polling components that run concurrently.

### 1. Energy Monitoring

**Script**: `scripts/poll_energymeter.py`
**Storage**: `data/energy.csv` and `data/energy.db`

This script collects real-time data from your P1 Energy Meter.

**Standard Command**:
```bash
python3 scripts/poll_energymeter.py -i 1m -o data/energy.csv
```

### 2. Room Temperature Monitoring

**Script**: `scripts/poll_evohome_standalone.py`
**Storage**: `data/rooms.csv` and `data/rooms.db`

Fetches temperatures for all Evohome zones.

**Standard Command**:
```bash
python3 scripts/poll_evohome_standalone.py -i 5m -o data/rooms.csv
```

### 3. Weather Monitoring

**Script**: `scripts/poll_openweathermap.py`
**Storage**: `data/weather.csv` and `data/weather.db`

Collects local weather data for correlation.

**Standard Command**:
```bash
python3 scripts/poll_openweathermap.py -i 10m -o data/weather.csv
```

## Data Analysis

### SQLite Database

All data is stored in SQLite databases located in the `data/` folder. This format is ideal for:
- Historical analysis
- Integration with Grafana (using the SQLite plugin)
- Fast querying of large datasets

**Example Query (Energy)**:
```bash
sqlite3 data/energy.db "SELECT timestamp, power_kwh FROM readings WHERE timestamp > '2025-01-01'"
```

### CSV Files

CSV files are also maintained for:
- Quick manual inspection in Excel or Sheets
- Simple data portability
- Backup/Archive purposes

## Troubleshooting

### Connectivity
- **API Timeout**: Check your internet connection or the local status of your P1 Meter.
- **Missing Data**: Ensure your `.env` credentials are correct.

### Log Files
Check `logs/monitor_all.log` for detailed error messages from the unified monitor.

## Advanced Usage

For running as a background service on macOS, please refer to the `README.md` section on launchd configuration.
