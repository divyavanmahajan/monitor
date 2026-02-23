from __future__ import annotations
import asyncio
import argparse
import os
from pathlib import Path
from .main import MasterController, PollingController
from .backends.sqlite import SQLiteBackend
from .backends.csv import CSVBackend
from .monitors.energy import EnergyMonitor

def main():
    parser = argparse.ArgumentParser(description="Poll P1 Energy Meter API and log energy data")
    parser.add_argument("-i", "--interval", default="5m", help="Polling interval")
    parser.add_argument("-o", "--output", default="data/energy.csv", help="Output CSV file path")
    args = parser.parse_args()
    
    output_path = Path(args.output)
    backends = [
        SQLiteBackend(output_path.with_suffix(".db")),
        CSVBackend(output_path.parent)
    ]
    
    # Energy Monitor (hardcoded URL for compatibility or take from env)
    source_name = "energy"
    api_url = os.getenv("ENERGY_API_URL", "http://p1meter-231dbe.local./api/v1/data")
    monitor = EnergyMonitor(source_name, args.interval, api_url)
    
    controller = PollingController(monitor, backends, args.interval)
    master = MasterController()
    master.add_controller(controller)
    
    try:
        asyncio.run(master.run_all())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
