from __future__ import annotations
import asyncio
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from .main import MasterController, PollingController
from .backends.sqlite import SQLiteBackend
from .backends.csv import CSVBackend
from .monitors.evohome import EvohomeMonitor

def main_cli():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Poll Evohome temperatures and log to CSV/SQLite")
    parser.add_argument("-i", "--interval", default="5m", help="Polling interval")
    parser.add_argument("-o", "--output", default="data/rooms.csv", help="Output CSV file path")
    args = parser.parse_args()
    
    username = os.getenv("EVOHOME_USERNAME") or os.getenv("EVOHOME_EMAIL")
    password = os.getenv("EVOHOME_PASSWORD")
    
    if not username or not password:
        print("Error: Evohome credentials not found.")
        return

    output_path = Path(args.output)
    backends = [
        SQLiteBackend(output_path.with_suffix(".db")),
        CSVBackend(output_path.parent)
    ]
    
    source_name = "evohome"
    monitor = EvohomeMonitor(source_name, args.interval, username, password)
    
    controller = PollingController(monitor, backends, args.interval)
    master = MasterController()
    master.add_controller(controller)
    
    try:
        asyncio.run(master.run_all())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main_cli()
