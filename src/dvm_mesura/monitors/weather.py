from __future__ import annotations
import aiohttp
from datetime import datetime, timezone
from typing import Any, Dict
from ..core.monitor import BaseMonitor

class WeatherMonitor(BaseMonitor):
    """Monitor for OpenWeatherMap API."""
    
    def __init__(self, name: str, interval: str, api_key: str, lat: str, lon: str):
        super().__init__(name, interval)
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.api_url = "https://api.openweathermap.org/data/3.0/onecall"

    async def fetch_data(self) -> Dict[str, Any]:
        url = f"{self.api_url}?lat={self.lat}&lon={self.lon}&exclude=minutely,hourly,daily,alerts&appid={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten weather data manually as in original script."""
        flattened: Dict[str, Any] = {}
        
        flattened["lat"] = data.get("lat")
        flattened["lon"] = data.get("lon")
        flattened["timezone"] = data.get("timezone")
        
        current = data.get("current", {})
        flattened["dt"] = current.get("dt")
        
        # Sunrise/Sunset
        for key in ["sunrise", "sunset"]:
            ts = current.get(key)
            if ts:
                flattened[key] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Temperature (Kelvin to Celsius)
        temp_k = current.get("temp")
        if temp_k is not None:
            flattened["temp_c"] = round(temp_k - 273.15, 2)
        
        flattened["pressure"] = current.get("pressure")
        flattened["humidity"] = current.get("humidity")
        flattened["uvi"] = current.get("uvi")
        flattened["clouds"] = current.get("clouds")
        flattened["visibility"] = current.get("visibility")
        flattened["wind_speed"] = current.get("wind_speed")
        
        weather = current.get("weather", [])
        if weather:
            w = weather[0]
            flattened["weather_main"] = w.get("main")
            flattened["weather_description"] = w.get("description")

        return flattened
