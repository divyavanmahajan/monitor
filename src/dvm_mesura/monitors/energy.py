from __future__ import annotations
import aiohttp
from typing import Any, Dict
from ..core.monitor import BaseMonitor
from ..core.helpers import flatten_dict

class EnergyMonitor(BaseMonitor):
    """Monitor for P1 Energy Meter."""
    
    def __init__(self, name: str, interval: str, api_url: str):
        super().__init__(name, interval)
        self.api_url = api_url

    async def fetch_data(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Flatten data, excluding "external" field as in original script
        return flatten_dict(data, exclude_fields={"external"})
