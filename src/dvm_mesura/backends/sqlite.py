from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Dict
from ..core.base import Backend

class SQLiteBackend(Backend):
    """SQLite backend with automatic schema evolution."""
    
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, data: Dict[str, Any], source_name: str) -> None:
        """Write data to a table named after the source_name."""
        table_name = source_name.replace("-", "_")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                table_exists = cursor.fetchone() is not None
                
                existing_cols = set()
                if table_exists:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    existing_cols = {row[1] for row in cursor.fetchall()}
                
                columns = list(data.keys())
                
                if not table_exists:
                    cols_sql = []
                    for k in columns:
                        val = data[k]
                        if isinstance(val, int):
                            col_type = "INTEGER"
                        elif isinstance(val, float):
                            col_type = "REAL"
                        else:
                            col_type = "TEXT"
                        cols_sql.append(f'"{k}" {col_type}')
                    
                    if not cols_sql:
                        return

                    create_sql = f'CREATE TABLE {table_name} ({", ".join(cols_sql)})'
                    cursor.execute(create_sql)
                else:
                    for k in columns:
                        if k not in existing_cols:
                            val = data[k]
                            if isinstance(val, int):
                                col_type = "INTEGER"
                            elif isinstance(val, float):
                                col_type = "REAL"
                            else:
                                col_type = "TEXT"
                            
                            try:
                                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{k}" {col_type}')
                            except sqlite3.OperationalError as e:
                                if "duplicate column" not in str(e).lower():
                                    raise

                placeholders = ", ".join(["?"] * len(columns))
                col_names = ", ".join([f'"{c}"' for c in columns])
                values = [data[c] for c in columns]
                
                cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)
                conn.commit()

        except Exception as e:
            print(f"Error writing to SQLite ({source_name}): {e}")
