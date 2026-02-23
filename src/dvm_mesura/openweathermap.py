from __future__ import annotations
import asyncio
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from .main import MasterController, PollingController
from .backends.sqlite import SQLiteBackend
from .backends.csv import CSVBackend
from .monitors.weather import WeatherMonitor

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Poll OpenWeatherMap API and log weather data")
    parser.add_argument("-i", "--interval", default="10m", help="Polling interval")
    parser.add_argument("-o", "--output", default="data/weatherdata.csv", help="Output CSV file path")
    args = parser.parse_args()
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY not found.")
        return

    output_path = Path(args.output)
    backends = [
        SQLiteBackend(output_path.with_suffix(".db")),
        CSVBackend(output_path.parent)
    ]
    
    source_name = "weather"
    monitor = WeatherMonitor(source_name, args.interval, api_key, lat="50.83172", lon="5.76712")
    
    controller = PollingController(monitor, backends, args.interval)
    master = MasterController()
    master.add_controller(controller)
    
    try:
        asyncio.run(master.run_all())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
