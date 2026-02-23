import pytest
import responses
import sqlite3
from pathlib import Path
from monitor.energymeter import fetch_energy_data, write_to_sqlite, API_URL

@responses.activate
def test_fetch_energy_data():
    """Test fetching energy data with a mocked API response."""
    mock_data = {
        "active_tariff": 2,
        "total_power_import_t1_kwh": 1000.123,
        "total_power_import_t2_kwh": 2000.456,
        "total_power_export_kwh": 500.789,
        "total_gas_m3": 1500.001
    }
    responses.add(responses.GET, API_URL, json=mock_data, status=200)
    
    data = fetch_energy_data()
    assert data == mock_data

def test_write_to_sqlite(tmp_path):
    """Test writing data to SQLite and automatic schema evolution."""
    # Setup temp file paths
    output_csv = tmp_path / "energy.csv"
    db_path = tmp_path / "energy.db"
    
    sample_data = {
        "timestamp": "2026-02-23T10:00:00Z",
        "active_tariff": 1,
        "total_power_import_t1_kwh": 10.5
    }
    
    # 1. Initial write (should create table)
    write_to_sqlite(sample_data, output_csv)
    
    assert db_path.exists()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM readings")
        rows = cursor.fetchall()
        assert len(rows) == 1
        # Check if active_tariff is there
        cursor.execute("PRAGMA table_info(readings)")
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
    write_to_sqlite(evolved_data, output_csv)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(readings)")
        cols = [row[1] for row in cursor.fetchall()]
        assert "new_utility_field" in cols
        
        cursor.execute("SELECT new_utility_field FROM readings WHERE timestamp=?", ("2026-02-23T10:10:00Z",))
        val = cursor.fetchone()[0]
        assert val == 42.5
