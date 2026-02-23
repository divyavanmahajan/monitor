import os
from pathlib import Path
from dotenv import load_dotenv, set_key

def setup_wizard():
    """Interactive setup wizard to configure .env file."""
    env_path = Path(".env")
    load_dotenv(env_path)
    
    print("=== DVM Mesura Setup Wizard ===")
    print("Press Enter to keep the default value [shown in brackets].\n")

    # Energy settings
    energy_url = input(f"Energy Meter API URL [{os.getenv('ENERGY_API_URL', 'http://p1meter-231dbe.local./api/v1/data')}]: ") or os.getenv('ENERGY_API_URL', 'http://p1meter-231dbe.local./api/v1/data')
    set_key(str(env_path), "ENERGY_API_URL", energy_url)

    # Weather settings
    weather_key = input(f"OpenWeatherMap API Key [{os.getenv('OPENWEATHER_API_KEY', '')}]: ") or os.getenv('OPENWEATHER_API_KEY', '')
    set_key(str(env_path), "OPENWEATHER_API_KEY", weather_key)
    
    lat = input(f"Latitude [{os.getenv('LATITUDE', '50.83172')}]: ") or os.getenv('LATITUDE', '50.83172')
    set_key(str(env_path), "LATITUDE", lat)
    
    lon = input(f"Longitude [{os.getenv('LONGITUDE', '5.76712')}]: ") or os.getenv('LONGITUDE', '5.76712')
    set_key(str(env_path), "LONGITUDE", lon)

    # Evohome settings
    evo_user = input(f"Evohome Username/Email [{os.getenv('EVOHOME_USERNAME', '')}]: ") or os.getenv('EVOHOME_USERNAME', '')
    set_key(str(env_path), "EVOHOME_USERNAME", evo_user)
    
    evo_pw = input(f"Evohome Password [{os.getenv('EVOHOME_PASSWORD', '')}]: ") or os.getenv('EVOHOME_PASSWORD', '')
    set_key(str(env_path), "EVOHOME_PASSWORD", evo_pw)

    print(f"\nConfiguration saved to {env_path.absolute()}")
    print("You can now run 'mesura-all' to start monitoring.")
