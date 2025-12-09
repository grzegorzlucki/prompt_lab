import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.geo_utils import calculate_distance, filter_stops_by_radius

# Test calculate_distance
print("Testing calculate_distance:")
print("-" * 50)

# Wroclaw: Plac Grunwaldzki to Rynek
lat1, lon1 = 51.1092, 17.0415
lat2, lon2 = 51.1099, 17.0335
distance = calculate_distance(lat1, lon1, lat2, lon2)
print(f"Distance from Plac Grunwaldzki to nearby point: {distance:.2f} meters")

# Known distance test (approx 1km)
lat1, lon1 = 51.1079, 17.0385
lat2, lon2 = 51.1141, 17.0301
distance = calculate_distance(lat1, lon1, lat2, lon2)
print(f"Distance between test points: {distance:.2f} meters")

print("\nTesting filter_stops_by_radius:")
print("-" * 50)

# Sample stops
stops = [
    {'stop_id': '1', 'stop_name': 'Plac Grunwaldzki', 'stop_lat': 51.1092, 'stop_lon': 17.0415},
    {'stop_id': '2', 'stop_name': 'Renoma', 'stop_lat': 51.1040, 'stop_lon': 17.0280},
    {'stop_id': '3', 'stop_name': 'Dominikański', 'stop_lat': 51.1099, 'stop_lon': 17.0335},
    {'stop_id': '4', 'stop_name': 'Far Stop', 'stop_lat': 51.2000, 'stop_lon': 17.2000},
]

start_lat, start_lon = 51.1079, 17.0385
filtered = filter_stops_by_radius(start_lat, start_lon, stops, radius=1000)

print(f"Stops within 1000m of ({start_lat}, {start_lon}):")
for stop in filtered:
    print(f"  - {stop['stop_name']}: {stop['distance']:.2f}m")

print(f"\nTotal stops found: {len(filtered)}/{len(stops)}")
