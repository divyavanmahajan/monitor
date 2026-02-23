import sqlite3
import argparse
from pathlib import Path

def get_columns(cursor, table, db_prefix=""):
    cursor.execute(f"PRAGMA {db_prefix}table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def merge_db(source_db_path, source_table, dest_db_path, dest_table):
    print(f"Merging {source_db_path} ({source_table}) into {dest_db_path} ({dest_table})...")
    
    conn_dest = sqlite3.connect(dest_db_path)
    conn_dest.execute(f"ATTACH DATABASE '{source_db_path}' AS source_db")
    cur = conn_dest.cursor()
    
    # Ensure destination table exists. If it doesn't, recreate it from source schema.
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{dest_table}';")
    if not cur.fetchone():
        print(f"Creating destination table '{dest_table}' based on source schema.")
        cur.execute(f"CREATE TABLE {dest_table} AS SELECT * FROM source_db.{source_table} WHERE 0")
        conn_dest.commit()
    
    dest_cols = get_columns(cur, dest_table)
    source_cols = get_columns(cur, source_table, "source_db.")
    
    # Find overlapping columns
    common_cols = [c for c in source_cols if c in dest_cols]
    if not common_cols:
        print("No matching columns. Cannot merge.\n")
        conn_dest.close()
        return
        
    cols_str = ", ".join(f'"{c}"' for c in common_cols)
    
    # Pre-calculate counts for accurate reporting
    cur.execute(f"SELECT COUNT(*) FROM {dest_table}")
    initial_count = cur.fetchone()[0]
    
    # We will insert only if timestamp is not already there
    if "timestamp" in common_cols:
        query = f"""
        INSERT INTO {dest_table} ({cols_str})
        SELECT {cols_str} FROM source_db.{source_table}
        WHERE timestamp NOT IN (SELECT timestamp FROM {dest_table})
        """
    else:
        # Fallback if no timestamp column exists
        query = f"""
        INSERT INTO {dest_table} ({cols_str})
        SELECT {cols_str} FROM source_db.{source_table}
        EXCEPT
        SELECT {cols_str} FROM {dest_table}
        """
        
    try:
        cur.execute(query)
        conn_dest.commit()
        
        cur.execute(f"SELECT COUNT(*) FROM {dest_table}")
        final_count = cur.fetchone()[0]
        inserted = final_count - initial_count
        
        print(f"Success! Inserted {inserted} new distinct rows.\n")
    except Exception as e:
        print(f"Error merging: {e}\n")
        
    conn_dest.close()

def main():
    parser = argparse.ArgumentParser(description="Merge individual monitor databases into a single database.")
    parser.add_argument("--data-dir", default="data", help="Data directory (default: data)")
    parser.add_argument("--target-db", default="monitor.db", help="Target database name (default: monitor.db)")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    target_path = data_dir / args.target_db
    
    if not data_dir.exists():
        print(f"Data directory '{data_dir}' not found.")
        return

    # Map (source_db_name, source_table) -> destination_table
    mappings = [
        ("energy.db", "energy", "energy"),
        ("weatherdata.db", "readings", "weather"),    # legacy script
        ("weather.db", "weather", "weather"),         # new script
        ("rooms.db", "readings", "evohome"),          # legacy script
        ("evohome.db", "evohome", "evohome"),         # new script
    ]
    
    print(f"Target Database: {target_path}\n" + "="*40)
    
    for db_name, src_table, dest_table in mappings:
        db_path = data_dir / db_name
        if db_path.exists():
            # Check if source table actually exists
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{src_table}';")
            has_table = cur.fetchone() is not None
            conn.close()
            
            if has_table:
                merge_db(str(db_path), src_table, str(target_path), dest_table)

if __name__ == "__main__":
    main()
