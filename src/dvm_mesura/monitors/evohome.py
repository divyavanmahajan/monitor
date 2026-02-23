from __future__ import annotations
import aiohttp
from typing import Any, Dict, List
from evohomeasync2 import EvohomeClient
from evohomeasync2.auth import AbstractTokenManager
from ..core.monitor import BaseMonitor

class SimpleTokenManager(AbstractTokenManager):
    """Simple token manager that stores tokens in memory."""
    async def save_access_token(self) -> None: pass
    async def _load_access_token(self) -> None: pass

class EvohomeMonitor(BaseMonitor):
    """Monitor for Honeywell Evohome."""
    
    def __init__(self, name: str, interval: str, username: str, password: str):
        super().__init__(name, interval)
        self.username = username
        self.password = password
        self.client: EvohomeClient | None = None
        self._session: aiohttp.ClientSession | None = None

    async def fetch_data(self) -> Dict[str, Any]:
        if not self._session:
            self._session = aiohttp.ClientSession()
            token_manager = SimpleTokenManager(self.username, self.password, self._session)
            self.client = EvohomeClient(token_manager)

        # Initial update or periodic update
        await self.client.update()
        loc = self.client.locations[0]
        await loc.update()
        
        # Return the location/system data structure
        return {"location": loc}

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        loc = data["location"]
        tcs = loc.gateways[0].systems[0]
        
        processed: Dict[str, Any] = {
            "system_mode": str(tcs.mode)
        }
        
        for zone in tcs.zones:
            col_name = f"_{zone.id}_{zone.name.replace(' ', '_')}"
            processed[col_name] = zone.temperature
            
        return processed

    async def cleanup(self):
        if self._session:
            await self._session.close()
            self._session = None
