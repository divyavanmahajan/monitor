from __future__ import annotations
import asyncio
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from dvm_mesura.core.controller import MasterController, PollingController
from dvm_mesura.backends.sqlite import SQLiteBackend
from dvm_mesura.backends.csv import CSVBackend
from dvm_mesura.monitors.energy import EnergyMonitor
from dvm_mesura.monitors.weather import WeatherMonitor
from dvm_mesura.monitors.evohome import EvohomeMonitor

def main():
    parser = argparse.ArgumentParser(description="Home Automation Monitoring Suite")
    parser.add_argument("--data-dir", default="data", help="Directory for data storage")
    parser.add_argument("--energy-api", default="http://p1meter-231dbe.local./api/v1/data", help="Energy meter API URL")
    parser.add_argument("--energy-interval", default="1m", help="Energy polling interval")
    parser.add_argument("--weather-interval", default="10m", help="Weather polling interval")
    parser.add_argument("--evohome-interval", default="5m", help="Evohome polling interval")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Backends
    sqlite_backend = SQLiteBackend(data_dir / "monitor.db")
    csv_backend = CSVBackend(data_dir)
    backends = [sqlite_backend, csv_backend]
    
    master = MasterController()
    
    # Energy Monitor
    energy = EnergyMonitor("energy", args.energy_interval, args.energy_api)
    master.add_controller(PollingController(energy, backends, args.energy_interval))
    
    # Weather Monitor
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_api_key:
        weather = WeatherMonitor("weather", args.weather_interval, weather_api_key, lat="50.83172", lon="5.76712")
        master.add_controller(PollingController(weather, backends, args.weather_interval))
    else:
        print("Warning: OPENWEATHER_API_KEY not found. Weather monitor skipped.")
        
    # Evohome Monitor
    evohome_user = os.getenv("EVOHOME_USERNAME") or os.getenv("EVOHOME_EMAIL")
    evohome_pw = os.getenv("EVOHOME_PASSWORD")
    if evohome_user and evohome_pw:
        evohome = EvohomeMonitor("evohome", args.evohome_interval, evohome_user, evohome_pw)
        master.add_controller(PollingController(evohome, backends, args.evohome_interval))
    else:
        print("Warning: Evohome credentials not found. Evohome monitor skipped.")
        
    print(f"Starting master controller with {len(master.controllers)} monitors...")
    asyncio.run(master.run_all())

if __name__ == "__main__":
    main()
