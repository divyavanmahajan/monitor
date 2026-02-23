import pytest
import asyncio
import sqlite3
import os
from pathlib import Path
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch
from dvm_mesura.core.helpers import parse_interval, format_time_display
from dvm_mesura.backends.sqlite import SQLiteBackend

def test_parse_interval():
    """Test interval string parsing."""
    assert parse_interval("10s") == 10.0
    assert parse_interval("1m") == 60.0
    assert parse_interval("10m") == 600.0
    assert parse_interval("120m") == 7200.0
    
    with pytest.raises(ValueError, match="at least 10 seconds"):
        parse_interval("5s")
    
    with pytest.raises(ValueError):
        parse_interval("h")
    with pytest.raises(ValueError):
        parse_interval("invalid")
    
    assert parse_interval("1h") == 3600
    with pytest.raises(ValueError):
        parse_interval("10x")
    with pytest.raises(ValueError, match="Invalid interval format"):
        parse_interval("invalid")

def test_format_time_display():
    """Test ISO timestamp formatting for display."""
    assert format_time_display("2026-02-23T10:00:00Z") == "23/02 10:00:00Z"
    assert format_time_display("2026-02-23T10:00:00+00:00") == "23/02 10:00:00Z"
    assert format_time_display(None) == "N/A"
    assert format_time_display("invalid") == "invalid"

@pytest.mark.asyncio
async def test_evohome_write_to_sqlite(tmp_path):
    """Test Evohome data persistence and schema evolution."""
    db_path = tmp_path / "rooms.db"
    
    sample_data = {
        "timestamp": "2026-02-23T10:00:00Z",
        "system_mode": "Auto",
        "_12345_Living_Room": 21.5
    }
    
    # 1. Initial write
    backend = SQLiteBackend(db_path)
    await backend.write(sample_data, "evohome")
    
    assert db_path.exists()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evohome")
        rows = cursor.fetchall()
        assert len(rows) == 1
        
        cursor.execute("PRAGMA table_info(evohome)")
        cols = [row[1] for row in cursor.fetchall()]
        assert "system_mode" in cols
        assert "_12345_Living_Room" in cols

    # 2. Schema evolution
    evolved_data = {
        "timestamp": "2026-02-23T10:10:00Z",
        "system_mode": "Auto",
        "_12345_Living_Room": 22.0,
        "_67890_Bedroom": 18.5
    }
    await backend.write(evolved_data, "evohome")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(evohome)")
        cols = [row[1] for row in cursor.fetchall()]
        assert "_67890_Bedroom" in cols
        
        cursor.execute("SELECT _67890_Bedroom FROM evohome WHERE timestamp=?", ("2026-02-23T10:10:00Z",))
        assert cursor.fetchone()[0] == 18.5

@pytest.mark.asyncio
async def test_evohome_monitor_logic():
    """Simple test for monitor logic."""
    from dvm_mesura.monitors.evohome import EvohomeMonitor
    monitor = EvohomeMonitor("rooms", "5m", "user", "pass")
    
    mock_zone = MagicMock()
    mock_zone.id = 123
    mock_zone.name = "Test"
    mock_zone.temperature = 20.5
    
    mock_system = MagicMock()
    mock_system.mode = "Auto"
    mock_system.zones = [mock_zone]
    
    mock_loc = MagicMock()
    mock_loc.gateways = [MagicMock(systems=[mock_system])]
    
    processed = monitor.process_data({"location": mock_loc})
    assert processed["_123_Test"] == 20.5
    assert processed["system_mode"] == "Auto"
