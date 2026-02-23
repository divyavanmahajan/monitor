from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol

class Backend(Protocol):
    """Protocol for storage backends."""
    def write(self, data: Dict[str, Any], source_name: str) -> None:
        """Write data to the storage backend."""
        ...

class Monitor(ABC):
    """Base class for all monitors."""
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from the source."""
        pass

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process/Flatten the source data."""
        return data
