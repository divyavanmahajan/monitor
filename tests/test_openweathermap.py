import pytest
import responses
import sqlite3
import os
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from dvm_mesura.monitors.weather import WeatherMonitor
from dvm_mesura.backends.sqlite import SQLiteBackend

@pytest.mark.asyncio
@responses.activate
async def test_fetch_weather_data():
    """Test fetching weather data with mocked API."""
    api_key = "test_key"
    mock_response = {
        "lat": 50.8,
        "current": {"temp": 280.15}
    }
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_ctx = AsyncMock()
        mock_ctx.raise_for_status = MagicMock()
        mock_ctx.json = AsyncMock(return_value=mock_response)
        mock_ctx.__aenter__.return_value = mock_ctx
        mock_get.return_value = mock_ctx
        
        monitor = WeatherMonitor("test", "10m", api_key, "50.8", "5.7")
        data = await monitor.fetch_data()
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
    monitor = WeatherMonitor("test", "10m", "key", "50.8", "5.7")
    flattened = monitor.process_data(mock_json)
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
    
    backend = SQLiteBackend(db_path)
    backend.write(weather_data, "weather")
    
    assert db_path.exists()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT temp_c FROM weather")
        assert cursor.fetchone()[0] == 15.5
