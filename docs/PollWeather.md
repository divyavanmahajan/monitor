# Poll OpenWeatherMap Script Documentation

The `poll_openweathermap.py` script continuously polls the OpenWeatherMap API and logs weather data to a CSV file, with optional on-screen display.

## Overview

The script fetches current weather data from OpenWeatherMap One Call API 3.0 at regular intervals and stores it in a flattened CSV format. It can display the data in a table format on screen.

## Location

The script is located at: `scripts/poll_openweathermap.py`

## Prerequisites

### Required Python Packages

- `requests`: For HTTP requests to the OpenWeatherMap API
  ```bash
  pip install requests
  ```

### Optional Packages

- `python-dotenv`: For loading API key from `.env` file (optional, falls back to environment variables)
  ```bash
  pip install python-dotenv
  ```

- `tabulate`: For better table formatting (optional, has fallback)
  ```bash
  pip install tabulate
  ```

## Usage

### Basic Usage

```bash
python3 scripts/poll_openweathermap.py -o weather.csv
```

This will:
- Poll the API every 10 minutes (default)
- Write data to `weather.csv`
- Display data on screen in a table
- Append to file if it already exists

### Command-Line Options

- **`-i`, `--interval`** (default: `10m`): Polling interval
  - Format: number followed by 'm' (minutes)
  - Valid range: 1m to 120m
  - Examples: `1m`, `5m`, `10m`, `30m`, `120m`

- **`-o`, `--output`** (required): Output CSV file path
  - Example: `weather.csv`, `data/weather_log.csv`

- **`-a`, `--append`** (flag): Explicitly append to existing file
  - This is the default behavior if file exists
  - Header will be skipped when appending

- **`--overwrite`** (flag): Overwrite existing file
  - Replaces existing file and writes header

- **`--noshow`** (flag): Do not display data on screen
  - Only write to CSV file
  - Useful for background logging


### Examples

```bash
# Poll every 5 minutes
python3 scripts/poll_openweathermap.py -i 5m -o weather.csv

# Poll every 30 minutes, append to existing file
python3 scripts/poll_openweathermap.py -i 30m -o weather.csv --append

# Poll every hour, no screen display
python3 scripts/poll_openweathermap.py -i 60m -o weather.csv --noshow

# Poll every 2 hours, overwrite existing file
python3 scripts/poll_openweathermap.py -i 120m -o weather.csv --overwrite

```

## CSV Output Format

The CSV file contains flattened weather data with the following columns:

### Column Structure

1. **`timestamp`**: ISO 8601 formatted timestamp when data was fetched
2. **`lat`**: Latitude (decimal degrees)
3. **`lon`**: Longitude (decimal degrees)
4. **`timezone`**: Timezone name (IANA format)
5. **`timezone_offset`**: Timezone offset in seconds from UTC
6. **`dt`**: Current time (Unix timestamp)
7. **`sunrise`**: Sunrise time (ISO 8601 format, e.g., `2025-01-15T07:30:00`)
8. **`sunset`**: Sunset time (ISO 8601 format, e.g., `2025-01-15T17:45:00`)
9. **`temp_k`**: Temperature in Kelvin
10. **`temp_c`**: Temperature in Celsius (converted from Kelvin)
11. **`feels_like_k`**: "Feels like" temperature in Kelvin
12. **`feels_like_c`**: "Feels like" temperature in Celsius
13. **`dew_point_k`**: Dew point in Kelvin
14. **`dew_point_c`**: Dew point in Celsius
15. **`pressure`**: Atmospheric pressure in hPa
16. **`humidity`**: Relative humidity percentage
17. **`uvi`**: UV index
18. **`clouds`**: Cloudiness percentage (0-100)
19. **`visibility`**: Visibility in meters
20. **`wind_speed`**: Wind speed in m/s
21. **`wind_deg`**: Wind direction in degrees
22. **`weather_id`**: Weather condition ID
23. **`weather_main`**: Main weather category
24. **`weather_description`**: Weather description
25. **`weather_icon`**: Weather icon code

### Example CSV Row

```csv
timestamp,lat,lon,timezone,timezone_offset,dt,sunrise,sunset,temp_k,temp_c,feels_like_k,feels_like_c,dew_point_k,dew_point_c,pressure,humidity,uvi,clouds,visibility,wind_speed,wind_deg,weather_id,weather_main,weather_description,weather_icon
2025-01-15T10:30:00.123456,50.8317,5.7671,Europe/Amsterdam,3600,1763512108,2025-01-15T07:30:00,2025-01-15T17:45:00,277.18,4.03,272.16,-0.99,275.53,2.38,1009,89,0,100,10000,7.72,190,804,Clouds,overcast clouds,04n
```

## Interactive Features

- **Press 'L'**: Display the table header again (useful when scrolling through data)
- **Press Ctrl+C**: Stop the script gracefully

## Screen Display

When `--noshow` is not specified, the script displays a table with the following columns:

- **Time**: Formatted as `dd/mm hh:mm` (e.g., `15/01 10:30`)
- **Temp (C)**: Temperature in Celsius with 1 decimal place
- **Pressure**: Atmospheric pressure in hPa
- **Humidity**: Relative humidity percentage
- **Clouds**: Cloudiness percentage

### Example Display

```
Weather Data - Updated: 2025-01-15 10:30:00

┌─────────────┬───────────┬──────────┬───────────┬─────────┐
│ Time        │ Temp (C)  │ Pressure │ Humidity  │ Clouds  │
├─────────────┼───────────┼──────────┼───────────┼─────────┤
│ 15/01 10:00 │ 4.0       │ 1009     │ 89%       │ 100%    │
│ 15/01 10:10 │ 4.1       │ 1008     │ 88%       │ 100%    │
│ 15/01 10:20 │ 4.2       │ 1009     │ 87%       │ 99%     │
│ 15/01 10:30 │ 4.0       │ 1009     │ 89%       │ 100%    │
└─────────────┴───────────┴──────────┴───────────┴─────────┘

Next update in 10m... (Press 'L' for header, Ctrl+C to stop)
```

The display shows the last 20 data points and refreshes after each API call.

## File Handling

### New Files

When creating a new CSV file:
- Header row is written immediately
- First data row is written after the first API call

### Appending to Existing Files

When appending to an existing file (default behavior):
- Header row is **not** written again
- New data rows are appended to the end
- Existing file structure is preserved

### Overwriting Existing Files

When overwriting an existing file (using `--overwrite`):
- Header row is written
- All previous data is replaced
- New data rows are written from the beginning


## API Configuration

The script uses the following API configuration:

- **API Endpoint**: `https://api.openweathermap.org/data/3.0/onecall`
- **Location**: 50.83172° N, 5.76712° E
- **API Key**: Read from environment variable `OPENWEATHER_API_KEY` or `.env` file
- **Exclude**: `minutely,hourly,daily,alerts` (current weather only)

### Setting the API Key

The API key can be provided in two ways:

1. **Environment Variable** (recommended for production):
   ```bash
   export OPENWEATHER_API_KEY=your_api_key_here
   python3 scripts/poll_openweathermap.py -o weather.csv
   ```

2. **`.env` File** (recommended for development):
   Create a `.env` file in the project root:
   ```bash
   # .env
   OPENWEATHER_API_KEY=your_api_key_here
   ```
   
   The script will automatically load the `.env` file if `python-dotenv` is installed:
   ```bash
   pip install python-dotenv
   ```
   
   If `python-dotenv` is not installed, the script will still work but only reads from environment variables.

### Changing the Location

To change the location, edit the constants at the top of `scripts/poll_openweathermap.py`:

```python
LAT = "50.83172"
LON = "5.76712"
```

## Error Handling

- **API Errors**: If the API call fails, the script logs an error and retries after the interval
- **Network Errors**: Network timeouts and connection errors are caught and logged
- **Keyboard Interrupt**: Press `Ctrl+C` to gracefully stop the script
- **File Errors**: File write errors are caught and displayed

## Data Analysis

### Reading the CSV File

**Python with pandas:**
```python
import pandas as pd

df = pd.read_csv('weather.csv', parse_dates=['timestamp'])
print(df.head())
print(df.describe())
```

**Python with csv module:**
```python
import csv

with open('weather.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Time: {row['timestamp']}, Temp: {row['temp_c']}°C")
```

### Plotting Temperature Trends

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('weather.csv', parse_dates=['timestamp'])
df['temp_c'] = pd.to_numeric(df['temp_c'])
df.plot(x='timestamp', y='temp_c', kind='line', title='Temperature Over Time')
plt.show()
```

## Notes

- The script runs continuously until interrupted with `Ctrl+C`
- The screen display is cleared and refreshed after each update
- The display shows the last 20 data points for readability
- All timestamps in the CSV are in ISO 8601 format
- Temperature values are converted from Kelvin to Celsius
- The script uses the same API endpoint and parameters as `get_weather.sh`
- File size grows continuously as data is logged
- The script can be run in the background with `--noshow` option

## Related Documentation

- See `docs/OpenWeatherMapJSON.md` for the JSON structure returned by the API
- See `scripts/get_weather.sh` for the curl script that fetches the same data
- [OpenWeatherMap One Call API 3.0 Documentation](https://openweathermap.org/api/one-call-3)

