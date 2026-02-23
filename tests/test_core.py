import pytest
import sqlite3
import csv
from pathlib import Path
from dvm_mesura.core.helpers import parse_interval, flatten_dict, format_time_display
from dvm_mesura.backends.sqlite import SQLiteBackend
from dvm_mesura.backends.csv import CSVBackend

def test_parse_interval():
    assert parse_interval("1m") == 60.0
    assert parse_interval("10s") == 10.0
    with pytest.raises(ValueError):
        parse_interval("invalid")

def test_flatten_dict():
    data = {"a": {"b": 1}, "c": [1, 2]}
    flattened = flatten_dict(data)
    assert flattened["a.b"] == 1
    assert flattened["c[0]"] == 1

def test_sqlite_backend(tmp_path):
    db_path = tmp_path / "test.db"
    backend = SQLiteBackend(db_path)
    data = {"timestamp": "2026-02-23T10:00:00Z", "val": 1.5}
    
    backend.write(data, "test_source")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT val FROM test_source")
        assert cursor.fetchone()[0] == 1.5

def test_csv_backend(tmp_path):
    backend = CSVBackend(tmp_path)
    data = {"timestamp": "2026-02-23T10:00:00Z", "val": 1.5}
    
    backend.write(data, "test_source")
    
    csv_file = tmp_path / "test_source.csv"
    assert csv_file.exists()
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        row = next(reader)
        assert float(row["val"]) == 1.5
