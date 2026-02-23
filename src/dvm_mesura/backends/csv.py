from __future__ import annotations
import asyncio
import csv
from pathlib import Path
from typing import Any, Dict
from ..core.base import Backend

class CSVBackend(Backend):
    """CSV backend with separate files per source."""
    
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def write(self, data: Dict[str, Any], source_name: str) -> None:
        """Write data to a CSV file named after the source_name."""
        csv_path = self.data_dir / f"{source_name}.csv"
        file_exists = csv_path.exists()
        
        try:
            # We use to_thread for file I/O to avoid blocking the event loop
            await asyncio.to_thread(self._sync_write, data, csv_path, file_exists)
        except Exception as e:
            print(f"Error writing to CSV ({source_name}): {e}")

    def _sync_write(self, data: Dict[str, Any], csv_path: Path, file_exists: bool) -> None:
        """Synchronous write implementation called via asyncio.to_thread."""
        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
