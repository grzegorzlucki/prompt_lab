import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
from datetime import datetime
from services.departure_service import DepartureService

print("Testing DepartureService:")
print("=" * 60)

# Connect to database
try:
    conn = sqlite3.connect('wroclaw_transport.db')
    service = DepartureService(conn)
    print("✓ Connected to database\n")
except Exception as e:
    print(f"✗ Failed to connect to database: {e}")
    exit(1)

# Test 1: Valid query
print("Test 1: Valid query with nearby stops")
print("-" * 60)
try:
    start_lat, start_lon = 51.1079, 17.0385
    end_lat, end_lon = 51.1141, 17.0301
    start_time = datetime(2025, 4, 2, 8, 30, 0)
    
    departures = service.get_closest_departures(
        start_lat, start_lon,
        end_lat, end_lon,
        start_time,
        limit=3,
        radius=1000
    )
    
    print(f"Found {len(departures)} departures")
    for i, dep in enumerate(departures, 1):
        print(f"\n{i}. Trip: {dep['trip_id']}")
        print(f"   Route: {dep['route_id']}")
        print(f"   Headsign: {dep['trip_headsign']}")
        print(f"   Stop: {dep['stop']['name']}")
        print(f"   Coordinates: ({dep['stop']['coordinates']['latitude']}, {dep['stop']['coordinates']['longitude']})")
        print(f"   Departure: {dep['stop']['departure_time']}")
    
    print("\n✓ Test passed")
except Exception as e:
    print(f"✗ Test failed: {e}")

# Test 2: Invalid coordinates
print("\n\nTest 2: Invalid coordinates")
print("-" * 60)
try:
    departures = service.get_closest_departures(
        200, 200,  # Invalid
        51.1141, 17.0301,
        datetime.now(),
        limit=5
    )
    print("✗ Test failed: Should have raised ValueError")
except ValueError as e:
    print(f"✓ Test passed: Caught ValueError - {e}")
except Exception as e:
    print(f"✗ Test failed with unexpected error: {e}")

# Test 3: Large radius
print("\n\nTest 3: Large radius (5000m)")
print("-" * 60)
try:
    departures = service.get_closest_departures(
        51.1079, 17.0385,
        51.1141, 17.0301,
        datetime(2025, 4, 2, 8, 0, 0),
        limit=5,
        radius=5000
    )
    print(f"Found {len(departures)} departures with 5km radius")
    print("✓ Test passed")
except Exception as e:
    print(f"✗ Test failed: {e}")

# Test 4: Time conversion
print("\n\nTest 4: Time conversion (HH:MM:SS to ISO 8601)")
print("-" * 60)
try:
    base_date = datetime(2025, 4, 2, 0, 0, 0)
    
    # Test normal time
    iso_time = service._convert_to_iso(base_date, "08:30:00")
    print(f"08:30:00 -> {iso_time}")
    assert iso_time == "2025-04-02T08:30:00Z"
    
    # Test time >= 24:00:00 (next day)
    iso_time = service._convert_to_iso(base_date, "25:30:00")
    print(f"25:30:00 -> {iso_time}")
    assert iso_time == "2025-04-03T01:30:00Z"
    
    print("✓ Test passed")
except Exception as e:
    print(f"✗ Test failed: {e}")

# Cleanup
conn.close()
print("\n" + "=" * 60)
print("All tests completed!")
