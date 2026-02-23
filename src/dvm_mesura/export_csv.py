import sqlite3
import argparse
import csv
from pathlib import Path

def get_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def export_table_to_csv(db_path, table_name, csv_path):
    print(f"Exporting table '{table_name}' from {db_path} to {csv_path}...")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    if not cur.fetchone():
        print(f"Table '{table_name}' does not exist in {db_path}. Skipping.\n")
        conn.close()
        return

    columns = get_columns(cur, table_name)
    
    # Export data
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
        
    print(f"Success! Exported {len(rows)} rows to {csv_path}.\n")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Export tables from monitor.db to separate CSV files.")
    parser.add_argument("--data-dir", default="data", help="Data directory (default: data)")
    parser.add_argument("--source-db", default="monitor.db", help="Source database name (default: monitor.db)")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    source_path = data_dir / args.source_db
    
    if not source_path.exists():
        print(f"Database '{source_path}' not found.")
        return

    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)

    # Map target CSV name -> source table
    mappings = [
        ("energy.csv", "energy"),
        ("weather.csv", "weather"),
        ("evohome.csv", "evohome"),
    ]
    
    print(f"Source Database: {source_path}\n" + "="*40)
    
    for csv_name, source_table in mappings:
        csv_path = data_dir / csv_name
        export_table_to_csv(str(source_path), source_table, str(csv_path))

if __name__ == "__main__":
    main()
