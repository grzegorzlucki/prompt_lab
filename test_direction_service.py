import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from services.direction_service import calculate_bearing, is_heading_towards_destination

print("Testing calculate_bearing:")
print("-" * 50)

# Test North direction
bearing = calculate_bearing(51.0, 17.0, 52.0, 17.0)
print(f"North (51.0,17.0 -> 52.0,17.0): {bearing:.2f}° (expected ~0°)")

# Test East direction
bearing = calculate_bearing(51.0, 17.0, 51.0, 18.0)
print(f"East (51.0,17.0 -> 51.0,18.0): {bearing:.2f}° (expected ~90°)")

# Test South direction
bearing = calculate_bearing(52.0, 17.0, 51.0, 17.0)
print(f"South (52.0,17.0 -> 51.0,17.0): {bearing:.2f}° (expected ~180°)")

# Test West direction
bearing = calculate_bearing(51.0, 18.0, 51.0, 17.0)
print(f"West (51.0,18.0 -> 51.0,17.0): {bearing:.2f}° (expected ~270°)")

print("\nTesting is_heading_towards_destination:")
print("-" * 50)

# Start and destination
start_lat, start_lon = 51.1079, 17.0385
end_lat, end_lon = 51.1141, 17.0301

# Trip heading North-West (towards destination)
trip_correct = [
    {'stop_lat': 51.1080, 'stop_lon': 17.0380},
    {'stop_lat': 51.1100, 'stop_lon': 17.0350},
    {'stop_lat': 51.1130, 'stop_lon': 17.0320}
]

result = is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_correct)
print(f"Trip heading North-West (correct direction): {result} (expected True)")

# Trip heading South-East (opposite direction)
trip_opposite = [
    {'stop_lat': 51.1080, 'stop_lon': 17.0380},
    {'stop_lat': 51.1050, 'stop_lon': 17.0420},
    {'stop_lat': 51.1020, 'stop_lon': 17.0450}
]

result = is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_opposite)
print(f"Trip heading South-East (opposite direction): {result} (expected False)")

# Trip heading East (perpendicular, should accept)
trip_perpendicular = [
    {'stop_lat': 51.1080, 'stop_lon': 17.0380},
    {'stop_lat': 51.1080, 'stop_lon': 17.0450},
    {'stop_lat': 51.1080, 'stop_lon': 17.0500}
]

result = is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_perpendicular)
print(f"Trip heading East (perpendicular): {result} (expected True)")

# Edge case: single stop
trip_single = [{'stop_lat': 51.1080, 'stop_lon': 17.0380}]
result = is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_single)
print(f"Single stop trip: {result} (expected True)")

# Edge case: empty stops
trip_empty = []
result = is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_empty)
print(f"Empty stops: {result} (expected True)")

print("\n" + "=" * 50)
print("All tests completed!")
