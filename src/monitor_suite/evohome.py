#!/usr/bin/env python3
"""
Standalone script to poll Evohome temperatures using evohome-async.
Based on evohome_cli/poll_evohome.py.
"""

import argparse
import asyncio
import csv
import logging
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

import aiohttp

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from evohomeasync2 import EvohomeClient
    from evohomeasync2.auth import AbstractTokenManager
    from evohomeasync2.exceptions import ApiRequestFailedError, AuthenticationFailedError
except ImportError:
    print("Error: evohome-async library not found. Please install it via pip:", file=sys.stderr)
    print("  pip install evohome-async", file=sys.stderr)
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_LOGGER = logging.getLogger("poll_evohome")


class SimpleTokenManager(AbstractTokenManager):
    """Simple token manager that stores tokens in memory."""

    def __init__(self, username, password, websession):
        super().__init__(username, password, websession)

    async def save_access_token(self) -> None:
        pass

    async def _load_access_token(self) -> None:
        pass


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
        _LOGGER.error(f"Error writing to SQLite: {e}")


def parse_interval(interval_str: str) -> float:
    """Parse interval string (e.g., '10s', '1m', '10m') to seconds.
    
    Valid range: 10s to 120m
    """
    match = re.match(r"^(\d+)([s|m])$", interval_str.lower())
    if not match:
        raise ValueError(f"Invalid interval format: {interval_str}. Use format like '30s', '1m', '10m'")
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == "s":
        seconds = value
    elif unit == "m":
        seconds = value * 60
    else:
        raise ValueError(f"Invalid unit: {unit}. Use 's' for seconds or 'm' for minutes")
    
    if seconds < 10:
        raise ValueError(f"Interval must be at least 10 seconds, got {seconds}s")
    if seconds > 7200:
        raise ValueError(f"Interval must be at most 120 minutes, got {seconds}s")
    
    return float(seconds)


def format_time_display(timestamp: str | None) -> str:
    """Format ISO timestamp as dd/mm hh:mm."""
    if timestamp is None:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%M:%SZ")
    except (ValueError, AttributeError):
        return str(timestamp)[:19] if timestamp else "N/A"


def display_table(data_rows: list[dict[str, Any]], zone_order: list[int], zone_names: dict[int, str], show_header: bool = True) -> None:
    """Display Evohome data as a table."""
    if not data_rows:
        return

    # Prepare headers
    headers = ["Time", "Mode"] + [zone_names[zid] for zid in zone_order]
    
    # Prepare table data
    table_data = []
    for row in data_rows:
        row_data = [format_time_display(row.get("timestamp")), row.get("system_mode", "N/A")]
        for zid in zone_order:
            col_name = f"_{zid}_{zone_names[zid].replace(' ', '_')}"
            temp = row.get(col_name)
            if temp is None or temp == "N/A":
                row_data.append("N/A")
            else:
                row_data.append(f"{float(temp):.1f}")
        table_data.append(row_data)

    if tabulate:
        if show_header:
            print(tabulate(table_data, headers=headers, tablefmt="simple"))
        else:
            print(tabulate(table_data, tablefmt="simple"))
    else:
        # Simple manual formatting fallback
        col_widths = [len(str(h)) for h in headers]
        for row in table_data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        if show_header:
            print(" | ".join(h.ljust(w) for h, w in zip(headers, col_widths)))
        
        for row in table_data:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))



async def main():
    parser = argparse.ArgumentParser(
        description="Poll Evohome temperatures and log to CSV/SQLite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        default="data/rooms.csv",
        help="Output CSV file path (default: data/rooms.csv)",
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

    # Output paths
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load .env
    if load_dotenv:
        env_path = Path(__file__).parent.parent / ".env" if (Path(__file__).parent.parent / ".env").exists() else Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
            _LOGGER.info(f"Loaded credentials from {env_path}")
        else:
            load_dotenv() 

    username = os.getenv("EVOHOME_USERNAME") or os.getenv("EVOHOME_EMAIL")
    password = os.getenv("EVOHOME_PASSWORD")
    
    if not username or not password:
        _LOGGER.error("Evohome credentials (EVOHOME_USERNAME/EVOHOME_PASSWORD) not found in environment.")
        sys.exit(1)

    # Store data rows for display
    data_rows: list[dict[str, Any]] = []
    
    # Keyboard interaction setup
    show_header_event = threading.Event()
    keyboard_thread_running = True
    keyboard_thread = None

    def read_keyboard():
        nonlocal keyboard_thread_running
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
            while keyboard_thread_running:
                time.sleep(0.5)

    if not args.noshow and sys.stdin.isatty():
        keyboard_thread = threading.Thread(target=read_keyboard, daemon=True)
        keyboard_thread.start()

    async with aiohttp.ClientSession() as websession:
        token_manager = SimpleTokenManager(username, password, websession)
        evo = EvohomeClient(token_manager)

        try:
            await evo.update()
            loc = evo.locations[0]
            if not loc.gateways or not loc.gateways[0].systems:
                _LOGGER.error("No compatible system found.")
                sys.exit(1)
            tcs = loc.gateways[0].systems[0]
        except Exception as e:
            _LOGGER.error(f"Failed to get initial configuration: {e}")
            sys.exit(1)
        
        _LOGGER.info(f"Successfully connected as {username}")

        # Zone info
        zones = {z.id: z.name for z in tcs.zones}
        zone_order = [z.id for z in tcs.zones]
        csv_columns = ["timestamp", "system_mode"] + [f"_{zid}_{name.replace(' ', '_')}" for zid, name in zones.items()]

        # File handling
        if args.overwrite and output_file.exists():
            _LOGGER.info(f"Overwriting {output_file}")
            output_file.unlink()

        if not output_file.exists():
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(csv_columns)
        else:
            # Load last entries for display if appending
            try:
                with open(output_file, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    all_rows = list(reader)
                    if all_rows:
                        data_rows.extend(all_rows[-19:])
            except Exception:
                pass

        rate_limit_hit = False
        retry_delay = 300

        try:
            while True:
                try:
                    await loc.update()
                    now = datetime.now(timezone.utc)
                    timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                    system_mode = str(tcs.mode)
                    
                    row_data = [timestamp, system_mode]
                    current_zones = {z.id: z for z in tcs.zones}
                    sqlite_data_raw = {"timestamp": timestamp, "system_mode": system_mode}
                    
                    for zid in zone_order:
                        zone = current_zones.get(zid)
                        col_name = f"_{zid}_{zones[zid].replace(' ', '_')}"
                        if zone:
                            temp = zone.temperature
                            row_data.append(f"{temp:.1f}" if temp is not None else "N/A")
                            sqlite_data_raw[col_name] = temp
                        else:
                            row_data.append("N/A")
                            sqlite_data_raw[col_name] = None
                            
                    # Write to CSV/SQLite
                    with open(output_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(row_data)
                    
                    write_to_sqlite(sqlite_data_raw, output_file)

                    # Update display data
                    dict_data = dict(zip(csv_columns, row_data))
                    data_rows.append(dict_data)
                    if len(data_rows) > 20:
                        data_rows.pop(0)

                    # Display
                    if not args.noshow:
                        os.system("clear" if os.name != "nt" else "cls")
                        print(f"Evohome Monitoring - Updated: {datetime.now(timezone.utc).strftime('%H:%M:%SZ')}")
                        show_header = show_header_event.is_set()
                        if show_header:
                            show_header_event.clear()
                        display_table(data_rows, zone_order, zones, show_header=show_header)
                        print(f"\nNext update in {args.interval}... (L for header, Ctrl+C to stop)")

                    rate_limit_hit = False
                    
                    # Sleep logic for keyboard responsiveness
                    elapsed = 0.0
                    while elapsed < interval_seconds:
                        if not args.noshow and show_header_event.is_set():
                            show_header_event.clear()
                            os.system("clear" if os.name != "nt" else "cls")
                            print(f"Evohome Monitoring - Updated: {datetime.now(timezone.utc).strftime('%H:%M:%SZ')}")
                            display_table(data_rows, zone_order, zones, show_header=True)
                            print(f"\nNext update in {args.interval}... (L for header, Ctrl+C to stop)")
                        
                        sleep_time = min(0.1, interval_seconds - elapsed)
                        await asyncio.sleep(sleep_time)
                        elapsed += sleep_time

                except (ApiRequestFailedError, aiohttp.ClientError) as e:
                    if "429" in str(e):
                        _LOGGER.warning(f"Rate limited. Waiting {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 3600)
                    else:
                        _LOGGER.warning(f"Poll failed: {e}")
                        await asyncio.sleep(interval_seconds)
                except Exception as e:
                    _LOGGER.error(f"Error in loop: {e}")
                    await asyncio.sleep(interval_seconds)
        finally:
            keyboard_thread_running = False

def main_cli():
    """CLI entry point for evohome monitoring."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main_cli()
