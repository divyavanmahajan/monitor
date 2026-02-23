import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import certifi
import subprocess

def setup_wizard(env_path: Path | None = None):
    """Interactive setup wizard to configure .env file."""
    if env_path is None:
        env_path = Path(".env")
    load_dotenv(env_path)
    
    print("=== DVM Mesura Setup Wizard ===")
    print("Press Enter to keep the default value [shown in brackets].\n")

    # Energy settings
    energy_url = input(f"Energy Meter API URL [{os.getenv('ENERGY_API_URL', 'http://p1meter-231dbe.local./api/v1/data')}]: ") or os.getenv('ENERGY_API_URL', 'http://p1meter-231dbe.local./api/v1/data')
    set_key(str(env_path), "ENERGY_API_URL", energy_url)
    
    energy_int = input(f"Energy Polling Interval [{os.getenv('ENERGY_INTERVAL', '1m')}]: ") or os.getenv('ENERGY_INTERVAL', '1m')
    set_key(str(env_path), "ENERGY_INTERVAL", energy_int)

    # Weather settings
    weather_key = input(f"OpenWeatherMap API Key [{os.getenv('OPENWEATHER_API_KEY', '')}]: ") or os.getenv('OPENWEATHER_API_KEY', '')
    set_key(str(env_path), "OPENWEATHER_API_KEY", weather_key)
    
    weather_int = input(f"Weather Polling Interval [{os.getenv('WEATHER_INTERVAL', '10m')}]: ") or os.getenv('WEATHER_INTERVAL', '10m')
    set_key(str(env_path), "WEATHER_INTERVAL", weather_int)
    
    lat = input(f"Latitude [{os.getenv('LATITUDE', '50.83172')}]: ") or os.getenv('LATITUDE', '50.83172')
    set_key(str(env_path), "LATITUDE", lat)
    
    lon = input(f"Longitude [{os.getenv('LONGITUDE', '5.76712')}]: ") or os.getenv('LONGITUDE', '5.76712')
    set_key(str(env_path), "LONGITUDE", lon)

    # Evohome settings
    evo_user = input(f"Evohome Username/Email [{os.getenv('EVOHOME_USERNAME', '')}]: ") or os.getenv('EVOHOME_USERNAME', '')
    set_key(str(env_path), "EVOHOME_USERNAME", evo_user)
    
    evo_pw = input(f"Evohome Password [{os.getenv('EVOHOME_PASSWORD', '')}]: ") or os.getenv('EVOHOME_PASSWORD', '')
    set_key(str(env_path), "EVOHOME_PASSWORD", evo_pw)
    
    evo_int = input(f"Evohome Polling Interval [{os.getenv('EVOHOME_INTERVAL', '5m')}]: ") or os.getenv('EVOHOME_INTERVAL', '5m')
    set_key(str(env_path), "EVOHOME_INTERVAL", evo_int)

    # General settings
    data_dir = input(f"Data Directory [{os.getenv('DATA_DIR', 'data')}]: ") or os.getenv('DATA_DIR', 'data')
    set_key(str(env_path), "DATA_DIR", data_dir)
    
    separate = input(f"Use separate databases? (true/false) [{os.getenv('SEPARATE_DBS', 'false')}]: ") or os.getenv('SEPARATE_DBS', 'false')
    set_key(str(env_path), "SEPARATE_DBS", separate.lower())

    print(f"\nConfiguration saved to {env_path.absolute()}")
    print("You can now run 'mesura-all' to start monitoring.")
    
    check_digicert()

def check_digicert():
    """Checks if DigiCert root CA is in certifi bundle (required for some legacy macOS versions)."""
    cert_path = certifi.where()
    try:
        with open(cert_path, 'r') as f:
            content = f.read()
            if "DigiCert High Assurance" not in content:
                print("\n" + "!" * 65)
                print("WARNING: DigiCert High Assurance Root CA missing from certifi bundle!")
                print("This is common on older macOS versions and causes SSL errors with Evohome.")
                print("\nTo fix this, run the following command:")
                print(f"curl -L https://cacerts.digicert.com/DigiCertHighAssuranceEVRootCA.pem >> {cert_path}")
                print("!" * 65 + "\n")
            else:
                print("\n[✔] SSL Certificate bundle verified (DigiCert CA found).")
    except Exception as e:
        print(f"Note: Could not verify SSL bundle: {e}")
