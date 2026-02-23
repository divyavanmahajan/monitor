import pytest
import asyncio
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from dvm_mesura.monitors.energy import EnergyMonitor
from dvm_mesura.backends.sqlite import SQLiteBackend
from dvm_mesura.core.helpers import flatten_dict

@pytest.mark.asyncio
async def test_fetch_energy_data():
    """Test fetching energy data with a mocked aiohttp response."""
    mock_data = {
        "active_tariff": 2,
        "total_power_import_kwh": 1.1,
        "total_power_import_t1_kwh": 2.2,
        "total_power_import_t2_kwh": 3.3,
        "total_power_export_kwh": 4.4,
        "total_gas_m3": 5.5
    }
    API_URL = "http://p1meter-231dbe.local./api/v1/data"
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_ctx = AsyncMock()
        mock_ctx.raise_for_status = MagicMock()
        mock_ctx.json = AsyncMock(return_value=mock_data)
        mock_ctx.__aenter__.return_value = mock_ctx
        mock_get.return_value = mock_ctx
        
        monitor = EnergyMonitor("test", "1m", API_URL)
        data = await monitor.fetch_data()
        processed = monitor.process_data(data)
        assert processed["active_tariff"] == 2
        assert processed["total_power_import_kwh"] == 1.1
        assert processed["total_power_import_t1_kwh"] == 2.2

@pytest.mark.asyncio
async def test_write_to_sqlite(tmp_path):
    """Test writing data to SQLite and automatic schema evolution."""
    # Setup temp file paths
    db_path = tmp_path / "energy.db"
    
    sample_data = {
        "timestamp": "2026-02-23T10:00:00Z",
        "active_tariff": 1,
        "total_power_import_t1_kwh": 10.5
    }
    
    backend = SQLiteBackend(db_path)
    await backend.write(sample_data, "energy")
    
    assert db_path.exists()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM energy")
        rows = cursor.fetchall()
        assert len(rows) == 1
        # Check if active_tariff is there
        cursor.execute("PRAGMA table_info(energy)")
        cols = [row[1] for row in cursor.fetchall()]
        assert "active_tariff" in cols
        assert "total_power_import_t1_kwh" in cols

    # 2. Add second reading with a NEW field (should evolve schema)
    evolved_data = {
        "timestamp": "2026-02-23T10:10:00Z",
        "active_tariff": 1,
        "total_power_import_t1_kwh": 11.0,
        "new_utility_field": 42.5
    }
    await backend.write(evolved_data, "energy")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(energy)")
        cols = [row[1] for row in cursor.fetchall()]
        assert "new_utility_field" in cols
        
        cursor.execute("SELECT new_utility_field FROM energy WHERE timestamp=?", ("2026-02-23T10:10:00Z",))
        val = cursor.fetchone()[0]
        assert val == 42.5
