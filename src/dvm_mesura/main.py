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
from dvm_mesura.setup import setup_wizard

def main():
    # Load environment variables early for argparse defaults
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Home Automation Monitoring Suite")
    parser.add_argument("--data-dir", default=os.getenv("DATA_DIR", "data"), help="Directory for data storage")
    parser.add_argument("--energy-api", default=os.getenv("ENERGY_API_URL", "http://p1meter-231dbe.local./api/v1/data"), help="Energy meter API URL")
    parser.add_argument("--energy-interval", default=os.getenv("ENERGY_INTERVAL", "1m"), help="Energy polling interval")
    parser.add_argument("--weather-interval", default=os.getenv("WEATHER_INTERVAL", "10m"), help="Weather polling interval")
    parser.add_argument("--evohome-interval", default=os.getenv("EVOHOME_INTERVAL", "5m"), help="Evohome polling interval")
    parser.add_argument("--lat", default=os.getenv("LATITUDE"), help="Latitude for weather data")
    parser.add_argument("--lon", default=os.getenv("LONGITUDE"), help="Longitude for weather data")
    parser.add_argument("--separate", action="store_true", default=os.getenv("SEPARATE_DBS", "false").lower() == "true", help="Store each monitor in a separate SQLite database")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup wizard")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_wizard()
        return
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Shared backends
    csv_backend = CSVBackend(data_dir)
    shared_sqlite = None if args.separate else SQLiteBackend(data_dir / "monitor.db")
    
    master = MasterController()
    
    def get_backends(name: str):
        if args.separate:
            return [csv_backend, SQLiteBackend(data_dir / f"{name}.db")]
        return [csv_backend, shared_sqlite]

    # Energy Monitor
    energy = EnergyMonitor("energy", args.energy_interval, args.energy_api)
    master.add_controller(PollingController(energy, get_backends("energy"), args.energy_interval))
    
    # Weather Monitor
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_api_key:
        lat = args.lat or os.getenv("LATITUDE", "50.83172")
        lon = args.lon or os.getenv("LONGITUDE", "5.76712")
        weather = WeatherMonitor("weather", args.weather_interval, weather_api_key, lat=lat, lon=lon)
        master.add_controller(PollingController(weather, get_backends("weather"), args.weather_interval))
    else:
        print("Warning: OPENWEATHER_API_KEY not found. Weather monitor skipped.")
        
    # Evohome Monitor
    evohome_user = os.getenv("EVOHOME_USERNAME") or os.getenv("EVOHOME_EMAIL")
    evohome_pw = os.getenv("EVOHOME_PASSWORD")
    if evohome_user and evohome_pw:
        evohome = EvohomeMonitor("evohome", args.evohome_interval, evohome_user, evohome_pw)
        master.add_controller(PollingController(evohome, get_backends("evohome"), args.evohome_interval))
    else:
        print("Warning: Evohome credentials not found. Evohome monitor skipped.")
        
    print(f"Starting master controller with {len(master.controllers)} monitors...")
    asyncio.run(master.run_all())

if __name__ == "__main__":
    main()
