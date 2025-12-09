import csv
import sqlite3
import os
from pathlib import Path

GTFS_DIR = "OtwartyWroclaw_rozklad_jazdy_GTFS"
DB_FILE = "wroclaw_transport.db"
BATCH_SIZE = 1000

def detect_type(value):
    """Detect SQLite type from value."""
    if not value or value == '':
        return 'TEXT'
    try:
        float(value)
        return 'REAL' if '.' in value else 'INTEGER'
    except ValueError:
        return 'TEXT'

def infer_schema(filepath, encoding='utf-8'):
    """Infer schema from CSV file."""
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Clean BOM from first column if present
        if headers[0].startswith('\ufeff'):
            headers[0] = headers[0].replace('\ufeff', '')
        
        # Sample rows to detect types
        type_votes = {h: [] for h in headers}
        for i, row in enumerate(reader):
            if i >= 100:  # Sample first 100 rows
                break
            for header, value in zip(headers, row):
                type_votes[header].append(detect_type(value))
        
        # Determine final type (prefer TEXT if mixed)
        schema = {}
        for header in headers:
            votes = type_votes[header]
            if not votes or 'TEXT' in votes:
                schema[header] = 'TEXT'
            elif all(v == 'REAL' for v in votes):
                schema[header] = 'REAL'
            elif all(v in ('INTEGER', 'REAL') for v in votes):
                schema[header] = 'REAL'
            else:
                schema[header] = 'TEXT'
        
        return headers, schema

def create_table(conn, table_name, headers, schema):
    """Create SQLite table."""
    columns = ', '.join([f'"{h}" {schema[h]}' for h in headers])
    conn.execute(f'DROP TABLE IF EXISTS {table_name}')
    conn.execute(f'CREATE TABLE {table_name} ({columns})')
    print(f"[OK] Created table: {table_name}")

def import_csv(conn, filepath, table_name, encoding='utf-8'):
    """Import CSV data into SQLite table."""
    headers, schema = infer_schema(filepath, encoding)
    create_table(conn, table_name, headers, schema)
    
    cursor = conn.cursor()
    rows_imported = 0
    batch = []
    
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        placeholders = ','.join(['?' for _ in headers])
        insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
        
        for row in reader:
            if not any(row):  # Skip empty rows
                continue
            batch.append(row)
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(insert_sql, batch)
                rows_imported += len(batch)
                batch = []
        
        # Insert remaining rows
        if batch:
            cursor.executemany(insert_sql, batch)
            rows_imported += len(batch)
    
    conn.commit()
    return rows_imported

def create_indexes(conn):
    """Create indexes on frequently queried columns."""
    indexes = [
        ('idx_stops_stop_id', 'stops', 'stop_id'),
        ('idx_trips_trip_id', 'trips', 'trip_id'),
        ('idx_stop_times_trip_id', 'stop_times', 'trip_id'),
        ('idx_stop_times_stop_id', 'stop_times', 'stop_id'),
        ('idx_stops_coords', 'stops', 'stop_lat, stop_lon'),
    ]
    
    for idx_name, table, columns in indexes:
        try:
            conn.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns})')
            print(f"[OK] Created index: {idx_name}")
        except sqlite3.OperationalError as e:
            print(f"[WARN] Skipped index {idx_name}: {e}")

def main():
    """Main import function."""
    print("=" * 60)
    print("GTFS Data Import to SQLite")
    print("=" * 60)
    
    # Check if GTFS directory exists
    if not os.path.exists(GTFS_DIR):
        print(f"[ERROR] Directory '{GTFS_DIR}' not found!")
        return
    
    # Remove existing database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"[OK] Removed existing database: {DB_FILE}")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    print(f"[OK] Connected to database: {DB_FILE}\n")
    
    # Files to import
    files_to_import = [
        ('stops.txt', 'stops'),
        ('trips.txt', 'trips'),
        ('stop_times.txt', 'stop_times'),
    ]
    
    stats = {}
    
    # Import each file
    for filename, table_name in files_to_import:
        filepath = os.path.join(GTFS_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"[WARN] File '{filename}' not found, skipping...")
            continue
        
        print(f"\nImporting {filename}...")
        try:
            rows = import_csv(conn, filepath, table_name, encoding='utf-8')
            stats[table_name] = rows
            print(f"[OK] Imported {rows:,} rows into {table_name}")
        except Exception as e:
            print(f"[ERROR] Error importing {filename}: {e}")
    
    # Create indexes
    print("\nCreating indexes...")
    create_indexes(conn)
    
    # Close connection
    conn.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    for table, rows in stats.items():
        print(f"{table:20s}: {rows:,} rows")
    print("=" * 60)
    print(f"[OK] Database created: {DB_FILE}")
    print("=" * 60)

if __name__ == '__main__':
    main()
