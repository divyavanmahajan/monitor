import pytest
import responses
import sqlite3
import os
from pathlib import Path
from dvm_mesura.openweathermap import fetch_weather_data, write_to_sqlite, flatten_weather_data

@responses.activate
def test_fetch_weather_data():
    """Test fetching weather data with mocked API."""
    api_key = "test_key"
    mock_response = {
        "lat": 50.8,
        "lon": 5.7,
        "current": {
            "temp": 280.15,  # 7.0 C
            "pressure": 1013,
            "humidity": 80,
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}]
        }
    }
    # OpenWeatherMap URL in the script includes query params
    import re
    responses.add(responses.GET, url=re.compile(r".*api.openweathermap.org.*"), json=mock_response, status=200)
    
    data = fetch_weather_data(api_key)
    assert data["lat"] == 50.8
    assert data["current"]["temp"] == 280.15

def test_flatten_weather_data():
    """Test the flattening of nested weather data."""
    mock_json = {
        "lat": 50.8,
        "current": {
            "dt": 1700000000,
            "temp": 283.15,  # 10.0 C
            "weather": [{"main": "Clouds", "description": "broken clouds"}]
        }
    }
    flattened = flatten_weather_data(mock_json)
    assert flattened["temp_c"] == 10.0
    assert flattened["weather_main"] == "Clouds"
    assert flattened["dt"] == 1700000000

def test_weather_write_to_sqlite(tmp_path):
    """Test weather data persistence and mocking context."""
    output_csv = tmp_path / "weather.csv"
    db_path = tmp_path / "weather.db"
    
    weather_data = {
        "dt": 1700000000,
        "temp_c": 15.5,
        "humidity": 60,
        "weather_main": "Clear"
    }
    
    write_to_sqlite(weather_data, output_csv)
    
    assert db_path.exists()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT temp_c FROM readings")
        assert cursor.fetchone()[0] == 15.5
