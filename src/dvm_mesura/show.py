import sqlite3
import argparse
from pathlib import Path

def show_table(db_path, table_name, num_rows):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if not cur.fetchone():
        print(f"Table '{table_name}' does not exist.")
        conn.close()
        return

    # Get columns
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    
    # Try to order by timestamp if exists, otherwise rowid
    order_col = "timestamp" if "timestamp" in columns else "rowid"
    
    query = f"SELECT * FROM {table_name} ORDER BY {order_col} DESC LIMIT ?"
    cur.execute(query, (num_rows,))
    rows = cur.fetchall()
    
    # Reverse rows to show them in chronological order
    rows.reverse()
    
    print(f"\n=== Table: {table_name} (Last {num_rows} records) ===")
    if not rows:
        print("No records found.")
    else:
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(columns)
        writer.writerows(rows)
        
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Show the latest rows from tables in the monitor database.")
    parser.add_argument("--data-dir", default="data", help="Directory where database is stored (default: data)")
    parser.add_argument("--db", default="monitor.db", help="Database file name (default: monitor.db)")
    parser.add_argument("-n", "--rows", type=int, default=5, help="Number of rows to show (default: 5)")
    parser.add_argument("--table", help="Specific table to show. If not provided, shows all predefined tables.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    db_path = data_dir / args.db

    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return
        
    tables_to_show = [args.table] if args.table else ["energy", "weather", "evohome"]
    
    for table in tables_to_show:
        show_table(str(db_path), table, args.rows)

if __name__ == "__main__":
    main()
