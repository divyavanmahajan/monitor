#!/usr/bin/env python3
"""Poll P1 Energy Meter API and log energy data to CSV."""

from __future__ import annotations

import argparse
import csv
import os
import re
import select
import sqlite3
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
    load_dotenv = None


# API configuration
API_URL = "http://p1meter-231dbe.local./api/v1/data"


def parse_interval(interval_str: str) -> float:
    """Parse interval string (e.g., '1m', '10m', '120m') to seconds.

    Valid range: 10s to 120m (10s to 7200s)
    """
    # Match pattern: number followed by 'm'
    match = re.match(r"^(\d+)([s|m])$", interval_str.lower())
    if not match:
        raise ValueError(
            f"Invalid interval format: {interval_str}. Use format like '1m', '10m', '120m'"
        )

    value, unit = match.groups()
    value = int(value)

    if unit == "s":
        seconds = value
    elif unit == "m":
        seconds = value * 60
    else:
        raise ValueError(f"Invalid unit: {unit}. Use 'm' for minutes")

    # Validate range: 10s to 120m (10s to 7200s)
    if seconds < 10:
        raise ValueError(f"Interval must be at least 1 minute, got {seconds}s")
    if seconds > 7200:  # 120 minutes
        raise ValueError(f"Interval must be at most 120 minutes, got {seconds}s")

    return float(seconds)


def fetch_energy_data() -> dict[str, Any]:
    """Fetch energy data from P1 Energy Meter API."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching energy data: {e}", file=sys.stderr)
        raise


def flatten_data(
    data: dict[str, Any], exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    """Flatten nested JSON structure to a flat dictionary, excluding specified fields.

    Args:
        data: The JSON data to flatten
        exclude_fields: Set of field names to exclude (e.g., {"external"})

    Returns:
        Flattened dictionary with dot-notation keys for nested values
    """
    if exclude_fields is None:
        exclude_fields = set()

    flattened: dict[str, Any] = {}

    def _flatten(obj: Any, prefix: str = "") -> None:
        """Recursively flatten nested structures."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Skip excluded fields
                if key in exclude_fields:
                    continue

                new_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, (dict, list)):
                    _flatten(value, new_key)
                else:
                    flattened[new_key] = value
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                if isinstance(item, (dict, list)):
                    _flatten(item, new_key)
                else:
                    flattened[new_key] = item
        else:
            # Primitive value
            if prefix:
                flattened[prefix] = obj
            else:
                # This shouldn't happen, but handle it
                flattened["value"] = obj

    _flatten(data)
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
                # cid, name, type, notnull, dflt_value, pk
                existing_cols = {row[1] for row in cursor.fetchall()}
            
            columns = list(data.keys())
            
            if not table_exists:
                # Create table
                cols_sql = []
                for k in columns:
                    val = data[k]
                    # Simple type inference
                    if isinstance(val, int):
                        col_type = "INTEGER"
                    elif isinstance(val, float):
                        col_type = "REAL"
                    else:
                        col_type = "TEXT"
                    cols_sql.append(f'"{k}" {col_type}')
                
                # Ensure we have at least one column (should be true if data is not empty)
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
                            # Handle case where column might have been added by another process
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



def format_time_display(timestamp: str | None) -> str:
    """Format ISO timestamp as dd/mm hh:mm."""
    if timestamp is None:
        return "N/A"
    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%MZ")
    except (ValueError, AttributeError):
        # If not ISO format, try to return as-is or format differently
        return str(timestamp)[:16] if timestamp else "N/A"


def get_display_fields(data_rows: list[dict[str, Any]]) -> list[str]:
    """Get the fields to display in the table.

    Returns a fixed list of fields in the specified order.
    """
    # Fixed list of fields to display (in order)
    display_fields = [
        "timestamp",
        "active_tariff",
        "total_gas_m3",
        "total_power_import_t1_kwh",
        "total_power_import_t2_kwh",
        "total_power_export_kwh",
    ]

    # Check which fields are actually available in the data
    if data_rows:
        available_fields = set(data_rows[0].keys())
        # Filter to only include fields that exist in the data
        display_fields = [f for f in display_fields if f in available_fields]

    return display_fields


def display_table(data_rows: list[dict[str, Any]], show_header: bool = True) -> None:
    """Display energy data as a table."""
    if not data_rows:
        return

    # Get fields to display (fixed list)
    display_fields = get_display_fields(data_rows)
    if not display_fields:
        print("No data to display")
        return

    # Prepare table data - each row is a new reading
    table_data = []
    for row in data_rows:
        row_data = []
        for field in display_fields:
            value = row.get(field)
            if value is None:
                row_data.append("N/A")
            elif isinstance(value, (int, float)):
                # Format numbers nicely - always show 3 decimal places
                row_data.append(f"{float(value):.3f}")
            elif isinstance(value, str):
                # Handle string values from CSV - try to convert to number if it looks numeric
                if field == "timestamp":
                    row_data.append(format_time_display(value))
                else:
                    # Try to convert to number for numeric fields
                    try:
                        # Strip whitespace and try float conversion
                        cleaned_value = value.strip()
                        num_value = float(cleaned_value)
                        # Always format with exactly 3 decimal places
                        row_data.append(f"{num_value:.3f}")
                    except (ValueError, TypeError):
                        # Not a number, treat as string
                        row_data.append(str(value)[:20])  # Truncate long strings
            else:
                # For other types, format as string
                if field == "timestamp":
                    row_data.append(format_time_display(str(value)))
                else:
                    row_data.append(str(value)[:20])  # Truncate long strings
        table_data.append(row_data)

    # Use field names as headers (clean them up and make readable)
    header_map = {
        "timestamp": "Time",
        "active_tariff": "Tariff",
        "total_gas_m3": "Gas (m³)",
        "total_power_import_t1_kwh": "Import T1 (kWh)",
        "total_power_import_t2_kwh": "Import T2 (kWh)",
        "total_power_export_kwh": "Export (kWh)",
    }
    headers = [
        header_map.get(field, field.replace("_", " ").title())
        for field in display_fields
    ]

    if tabulate:
        if show_header:
            print(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            # Just show data without header
            print(tabulate(table_data, tablefmt="simple"))
    else:
        # Simple table without tabulate
        col_widths = [
            max(
                len(str(h)),
                max(len(str(row[i])) for row in table_data) if table_data else 0,
            )
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
        description="Poll P1 Energy Meter API and log energy data to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -o energy.csv
  %(prog)s -i 5m -o energy.csv
  %(prog)s -i 30m -o energy.csv --append
  %(prog)s -i 60m -o energy.csv --noshow
        """,
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=str,
        default="1m",
        help="Polling interval (1m to 120m, default: 1m)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="data/energy.csv",
        help="Output CSV file path (default: data/energy.csv)",
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

    # Check if file exists and ensure directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
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

    print(f"\nPolling P1 Energy Meter API every {args.interval}...")
    print(f"API URL: {API_URL}")
    print(f"Output file: {args.output}")
    if not args.noshow and sys.stdin.isatty():
        print("Press 'L' to show header, Ctrl+C to stop\n")
    else:
        print("Press Ctrl+C to stop\n")

    try:
        while True:
            # Fetch energy data
            try:
                energy_json = fetch_energy_data()

                # Flatten data, excluding "external" field
                flattened = flatten_data(energy_json, exclude_fields={"external"})

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
                        f"Energy Meter Data - Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n"
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
                            f"Energy Meter Data - Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n"
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
                print("\n\nStopping energy meter polling...")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                print(f"Retrying in {args.interval}...")
                time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nStopping energy meter polling...")
    finally:
        keyboard_thread_running = False
        if keyboard_thread and keyboard_thread.is_alive():
            keyboard_thread.join(timeout=1.0)

    print("Finished.")


if __name__ == "__main__":
    main()
