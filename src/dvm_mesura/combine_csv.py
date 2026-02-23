import sqlite3
import argparse
import csv
from pathlib import Path

def get_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def merge_csv_to_db(csv_path, dest_db_path, dest_table):
    print(f"Merging {csv_path} into {dest_db_path} ({dest_table})...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print(f"CSV {csv_path} is empty.\n")
            return
            
        csv_rows = list(reader)

    if not headers:
        print(f"CSV {csv_path} is empty.\n")
        return

    conn = sqlite3.connect(dest_db_path)
    cur = conn.cursor()
    
    # Ensure destination table exists.
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{dest_table}';")
    if not cur.fetchone():
        print(f"Creating destination table '{dest_table}' based on CSV schema.")
        cols_def = ", ".join([f'"{h}"' for h in headers])
        cur.execute(f"CREATE TABLE {dest_table} ({cols_def})")
        conn.commit()
        
    dest_cols = get_columns(cur, dest_table)
    
    common_cols = [c for c in headers if c in dest_cols]
    if not common_cols:
        print("No matching columns between CSV and table. Cannot merge.\n")
        conn.close()
        return

    # To avoid duplicates, get existing timestamps
    existing_timestamps = set()
    if "timestamp" in dest_cols:
        cur.execute(f'SELECT "timestamp" FROM {dest_table}')
        existing_timestamps = {row[0] for row in cur.fetchall()}

    timestamp_index = headers.index("timestamp") if "timestamp" in headers else -1

    # Prepare batch insert
    inserted = 0
    cols_str = ", ".join(f'"{c}"' for c in common_cols)
    placeholders = ", ".join(["?"] * len(common_cols))
    query = f"INSERT INTO {dest_table} ({cols_str}) VALUES ({placeholders})"

    # Filter rows
    rows_to_insert = []
    for row in csv_rows:
        if len(row) != len(headers):
            continue # skip malformed
        
        # Check timestamp
        if timestamp_index != -1:
            ts = row[timestamp_index]
            if ts in existing_timestamps:
                continue
            existing_timestamps.add(ts) # prevent duplicates within the CSV itself

        # build row dict
        row_dict = dict(zip(headers, row))
        insert_tuple = tuple(row_dict[c] for c in common_cols)
        rows_to_insert.append(insert_tuple)

    if rows_to_insert:
        try:
            cur.executemany(query, rows_to_insert)
            conn.commit()
            inserted = len(rows_to_insert)
            print(f"Success! Inserted {inserted} new distinct rows.\n")
        except Exception as e:
            print(f"Error merging: {e}\n")
    else:
        print("Success! Inserted 0 new distinct rows.\n")
        
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Merge individual monitor CSV files into a single database.")
    parser.add_argument("--data-dir", default="data", help="Data directory (default: data)")
    parser.add_argument("--target-db", default="monitor.db", help="Target database name (default: monitor.db)")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    target_path = data_dir / args.target_db
    
    if not data_dir.exists():
        print(f"Data directory '{data_dir}' not found.")
        return

    # Map csv_filename -> destination_table
    mappings = [
        ("energy.csv", "energy"),
        ("weatherdata.csv", "weather"),
        ("weather.csv", "weather"),
        ("temp.csv", "evohome"),
        ("rooms.csv", "evohome"),
        ("evohome.csv", "evohome"),
    ]
    
    print(f"Target Database: {target_path}\n" + "="*40)
    
    for csv_name, dest_table in mappings:
        csv_path = data_dir / csv_name
        if csv_path.exists():
            merge_csv_to_db(str(csv_path), str(target_path), dest_table)

if __name__ == "__main__":
    main()
