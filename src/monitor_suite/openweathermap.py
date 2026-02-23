#!/usr/bin/env python3
"""Poll OpenWeatherMap API and log weather data to CSV."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import os
import re
import select
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    # Fallback if tabulate is not available
    tabulate = None

try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback if python-dotenv is not available
    load_dotenv = None



# API configuration
API_URL = "https://api.openweathermap.org/data/3.0/onecall"
LAT = "50.83172"
LON = "5.76712"
EXCLUDE = "minutely,hourly,daily,alerts"


def get_api_key() -> str:
    """Get API key from environment variable or .env file."""
    # Try to load from .env file if python-dotenv is available
    if load_dotenv:
        # Load .env file from project root (parent of scripts directory)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        print(
            "Error: OPENWEATHER_API_KEY not found in environment or .env file",
            file=sys.stderr,
        )
        print(
            "Please set OPENWEATHER_API_KEY environment variable or create a .env file with:",
            file=sys.stderr,
        )
        print("  OPENWEATHER_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)

    return api_key


def parse_interval(interval_str: str) -> float:
    """Parse interval string (e.g., '1m', '10m', '120m') to seconds.

    Valid range: 1m to 120m (60s to 7200s)
    """
    # Match pattern: number followed by 'm'
    match = re.match(r"^(\d+)([m])$", interval_str.lower())
    if not match:
        raise ValueError(
            f"Invalid interval format: {interval_str}. Use format like '1m', '10m', '120m'"
        )

    value, unit = match.groups()
    value = int(value)

    if unit == "m":
        seconds = value * 60
    else:
        raise ValueError(f"Invalid unit: {unit}. Use 'm' for minutes")

    # Validate range: 1m to 120m (60s to 7200s)
    if seconds < 60:
        raise ValueError(f"Interval must be at least 1 minute, got {seconds}s")
    if seconds > 7200:  # 120 minutes
        raise ValueError(f"Interval must be at most 120 minutes, got {seconds}s")

    return float(seconds)


def fetch_weather_data(api_key: str) -> dict[str, Any]:
    """Fetch weather data from OpenWeatherMap API."""
    url = f"{API_URL}?lat={LAT}&lon={LON}&exclude={EXCLUDE}&appid={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}", file=sys.stderr)
        raise


def flatten_weather_data(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested weather JSON structure to a flat dictionary."""
    flattened: dict[str, Any] = {}

    # Top-level fields
    flattened["lat"] = data.get("lat")
    flattened["lon"] = data.get("lon")
    flattened["timezone"] = data.get("timezone")
    flattened["timezone_offset"] = data.get("timezone_offset")

    # Current weather fields
    current = data.get("current", {})

    # Time fields
    dt_timestamp = current.get("dt")
    flattened["dt"] = dt_timestamp

    # Convert sunrise and sunset from Unix timestamp to ISO 8601 format
    sunrise_timestamp = current.get("sunrise")
    if sunrise_timestamp is not None:
        flattened["sunrise"] = datetime.fromtimestamp(sunrise_timestamp, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        flattened["sunrise"] = None

    sunset_timestamp = current.get("sunset")
    if sunset_timestamp is not None:
        flattened["sunset"] = datetime.fromtimestamp(sunset_timestamp, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        flattened["sunset"] = None

    # Temperature fields (convert Kelvin to Celsius)
    temp_k = current.get("temp")
    if temp_k is not None:
        flattened["temp_k"] = temp_k
        flattened["temp_c"] = round(temp_k - 273.15, 2)
    else:
        flattened["temp_k"] = None
        flattened["temp_c"] = None

    feels_like_k = current.get("feels_like")
    if feels_like_k is not None:
        flattened["feels_like_k"] = feels_like_k
        flattened["feels_like_c"] = round(feels_like_k - 273.15, 2)
    else:
        flattened["feels_like_k"] = None
        flattened["feels_like_c"] = None

    dew_point_k = current.get("dew_point")
    if dew_point_k is not None:
        flattened["dew_point_k"] = dew_point_k
        flattened["dew_point_c"] = round(dew_point_k - 273.15, 2)
    else:
        flattened["dew_point_k"] = None
        flattened["dew_point_c"] = None

    # Atmospheric fields
    flattened["pressure"] = current.get("pressure")
    flattened["humidity"] = current.get("humidity")
    flattened["uvi"] = current.get("uvi")
    flattened["clouds"] = current.get("clouds")
    flattened["visibility"] = current.get("visibility")

    # Wind fields
    flattened["wind_speed"] = current.get("wind_speed")
    flattened["wind_deg"] = current.get("wind_deg")

    # Weather description
    weather = current.get("weather", [])
    if weather and len(weather) > 0:
        weather_obj = weather[0]
        flattened["weather_id"] = weather_obj.get("id")
        flattened["weather_main"] = weather_obj.get("main")
        flattened["weather_description"] = weather_obj.get("description")
        flattened["weather_icon"] = weather_obj.get("icon")
    else:
        flattened["weather_id"] = None
        flattened["weather_main"] = None
        flattened["weather_description"] = None
        flattened["weather_icon"] = None

    return flattened


def write_to_sqlite(data: dict[str, Any], csv_path: str | Path) -> None:
    """Write data to SQLite database.
    
    The database file will have the same name as the CSV file but with .db extension.
    Table name is 'readings'.
    Schema is automatically evolved to match new fields in data.
    """
    db_path = Path(csv_path).with_suffix(".db")
    table_name = "readings"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get existing columns if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            table_exists = cursor.fetchone() is not None
            
            existing_cols = set()
            if table_exists:
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_cols = {row[1] for row in cursor.fetchall()}
            
            columns = list(data.keys())
            
            if not table_exists:
                # Create table
                cols_sql = []
                for k in columns:
                    val = data[k]
                    if isinstance(val, int):
                        col_type = "INTEGER"
                    elif isinstance(val, float):
                        col_type = "REAL"
                    else:
                        col_type = "TEXT"
                    cols_sql.append(f'"{k}" {col_type}')
                
                if not cols_sql:
                    return

                create_sql = f'CREATE TABLE {table_name} ({", ".join(cols_sql)})'
                cursor.execute(create_sql)
            else:
                # Check for new columns and alter table
                for k in columns:
                    if k not in existing_cols:
                        val = data[k]
                        if isinstance(val, int):
                            col_type = "INTEGER"
                        elif isinstance(val, float):
                            col_type = "REAL"
                        else:
                            col_type = "TEXT"
                        
                        try:
                            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{k}" {col_type}')
                        except sqlite3.OperationalError as e:
                            if "duplicate column" not in str(e).lower():
                                raise

            # Insert data
            placeholders = ", ".join(["?"] * len(columns))
            col_names = ", ".join([f'"{c}"' for c in columns])
            values = [data[c] for c in columns]
            
            cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)
            conn.commit()

    except Exception as e:
        print(f"Error writing to SQLite: {e}", file=sys.stderr)


def format_time_display(timestamp: int | str | None) -> str:
    """Format Unix timestamp as dd/mm hh:mm."""
    if timestamp is None:
        return "N/A"
    # Handle string values from CSV
    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except (ValueError, TypeError):
            return "N/A"
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%d/%m %H:%MZ")


def display_table(data_rows: list[dict[str, Any]], show_header: bool = True) -> None:
    """Display weather data as a table."""
    if not data_rows:
        return

    # Prepare table data
    table_data = []
    for row in data_rows:
        timestamp = row.get("dt")
        time_str = format_time_display(timestamp)

        # Convert string values from CSV to numbers if needed
        temp_c = row.get("temp_c")
        if isinstance(temp_c, str):
            try:
                temp_c = float(temp_c)
            except (ValueError, TypeError):
                temp_c = None
        temp_str = f"{temp_c:.1f}" if temp_c is not None else "N/A"

        pressure = row.get("pressure")
        if isinstance(pressure, str):
            try:
                pressure = float(pressure)
            except (ValueError, TypeError):
                pressure = None
        pressure_str = str(pressure) if pressure is not None else "N/A"

        humidity = row.get("humidity")
        if isinstance(humidity, str):
            try:
                humidity = float(humidity)
            except (ValueError, TypeError):
                humidity = None
        humidity_str = f"{humidity}%" if humidity is not None else "N/A"

        clouds = row.get("clouds")
        if isinstance(clouds, str):
            try:
                clouds = float(clouds)
            except (ValueError, TypeError):
                clouds = None
        clouds_str = f"{clouds}%" if clouds is not None else "N/A"

        table_data.append([time_str, temp_str, pressure_str, humidity_str, clouds_str])

    headers = ["Time", "Temp (C)", "Pressure", "Humidity", "Clouds"]

    if tabulate:
        if show_header:
            print(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Just show data without header
            print(tabulate(table_data, tablefmt="simple"))
    else:
        # Simple table without tabulate
        col_widths = [
            max(len(str(h)), max(len(str(row[i])) for row in table_data))
            for i, h in enumerate(headers)
        ]

        # Print header if requested
        if show_header:
            header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
            print(header_row)

        # Print data rows
        for row in table_data:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Poll OpenWeatherMap API and log weather data to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -o weather.csv
  %(prog)s -i 5m -o weather.csv
  %(prog)s -i 30m -o weather.csv --append
  %(prog)s -i 60m -o weather.csv --noshow
        """,
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=str,
        default="10m",
        help="Polling interval (1m to 120m, default: 10m)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output CSV file path",
    )

    parser.add_argument(
        "-a",
        "--append",
        action="store_true",
        help="Append to existing file (default: append if file exists)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing file (default: append if file exists)",
    )

    parser.add_argument(
        "--noshow",
        action="store_true",
        help="Do not display data on screen",
    )


    args = parser.parse_args()

    # Parse interval
    try:
        interval_seconds = parse_interval(args.interval)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if file exists
    output_path = Path(args.output)
    file_exists = output_path.exists()
    write_header = True

    # Store data rows for display
    data_rows: list[dict[str, Any]] = []


    if file_exists:
        if args.overwrite:
            print(f"Overwriting existing file: {args.output}")
            write_header = True
        else:
            print(f"Appending to existing file: {args.output} (header will be skipped)")
            write_header = False
            # Read last 3 entries from existing CSV file
            try:
                with open(output_path, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    all_rows = list(reader)
                    if all_rows:
                        # Get last 3 rows (or fewer if less than 3 exist)
                        last_rows = all_rows[-3:]
                        data_rows.extend(last_rows)
                        print(f"Loaded {len(last_rows)} previous entries from CSV file")
            except Exception as e:
                print(
                    f"Warning: Could not read existing CSV file: {e}", file=sys.stderr
                )


    # Setup keyboard input handling for 'L' key
    show_header_event = threading.Event()
    keyboard_thread_running = True
    keyboard_thread: threading.Thread | None = None

    def read_keyboard():
        """Read keyboard input in a separate thread."""
        nonlocal keyboard_thread_running

        # Try to set up non-blocking stdin (Unix-like systems)
        try:
            import termios
            import tty

            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

            try:
                while keyboard_thread_running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        char = sys.stdin.read(1)
                        if char.lower() == "l":
                            show_header_event.set()
                    time.sleep(0.1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except (ImportError, OSError, AttributeError):
            # Fallback for systems without termios (e.g., Windows)
            # On Windows or systems without termios, keyboard input won't work
            # Just sleep to keep thread alive
            while keyboard_thread_running:
                time.sleep(0.5)

    # Start keyboard thread only if showing on screen AND stdin is a TTY
    if not args.noshow and sys.stdin.isatty():
        keyboard_thread = threading.Thread(target=read_keyboard, daemon=True)
        keyboard_thread.start()

    # Get API key from environment or .env file
    api_key = get_api_key()

    print(f"\nPolling OpenWeatherMap API every {args.interval}...")
    print(f"Output file: {args.output}")
    if not args.noshow and sys.stdin.isatty():
        print("Press 'L' to show header, Ctrl+C to stop\n")
    else:
        print("Press Ctrl+C to stop\n")

    try:
        while True:
            # Fetch weather data
            try:
                weather_json = fetch_weather_data(api_key)
                flattened = flatten_weather_data(weather_json)

                # Add current timestamp in UTC with Z suffix
                timestamp = datetime.now(timezone.utc)
                flattened["timestamp"] = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')


                # Write to SQLite
                write_to_sqlite(flattened, output_path)

                # Write to CSV
                file_mode = "w" if write_header else "a"
                with open(output_path, file_mode, newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=flattened.keys())
                    if write_header:
                        writer.writeheader()
                        write_header = False
                    writer.writerow(flattened)

                # Add to display data (keep last 20 rows for display)
                data_rows.append(flattened)
                if len(data_rows) > 20:
                    data_rows.pop(0)

                # Display table
                if not args.noshow:
                    # Clear screen and show table
                    os.system("clear" if os.name != "nt" else "cls")
                    print(
                        f"Weather Data - Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n"
                    )

                    # Check if 'L' was pressed to show header
                    show_header = show_header_event.is_set()
                    if show_header:
                        show_header_event.clear()

                    display_table(data_rows, show_header=show_header)
                    print(
                        f"\nNext update in {args.interval}... (Press 'L' for header, Ctrl+C to stop)"
                    )

                # Wait for interval, but check for 'L' key press periodically
                elapsed = 0.0
                check_interval = 0.1  # Check every 100ms
                while elapsed < interval_seconds:
                    # Check for 'L' key press
                    if not args.noshow and show_header_event.is_set():
                        show_header_event.clear()
                        # Redisplay with header
                        os.system("clear" if os.name != "nt" else "cls")
                        print(
                            f"Weather Data - Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n"
                        )
                        display_table(data_rows, show_header=True)
                        print(
                            f"\nNext update in {args.interval}... (Press 'L' for header, Ctrl+C to stop)"
                        )

                    # Sleep in small increments to allow responsive 'L' key handling
                    sleep_time = min(check_interval, interval_seconds - elapsed)
                    time.sleep(sleep_time)
                    elapsed += sleep_time

            except KeyboardInterrupt:
                print("\n\nStopping weather polling...")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                print(f"Retrying in {args.interval}...")
                time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nStopping weather polling...")
    finally:
        keyboard_thread_running = False
        if keyboard_thread and keyboard_thread.is_alive():
            keyboard_thread.join(timeout=1.0)

    print("Finished.")


if __name__ == "__main__":
    main()
