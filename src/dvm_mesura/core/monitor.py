from __future__ import annotations
from typing import Any, Dict
from .base import Backend
from .helpers import flatten_dict

class BaseMonitor:
    def __init__(self, name: str, interval: str):
        self.name = name
        self.interval_str = interval
        
    async def fetch_data(self) -> Dict[str, Any]:
        raise NotImplementedError

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return flatten_dict(data)
