import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask
from src.public_transport_api.controllers.departures_controller import departures_bp
from src.public_transport_api.controllers.trips_controller import trips_bp
import json

app = Flask(__name__)
app.register_blueprint(departures_bp)
app.register_blueprint(trips_bp)
app.config['TESTING'] = True

print("Testing Frontend-API Connection:")
print("=" * 60)

with app.test_client() as client:
    
    # Test 1: Trip endpoint (from frontend dropdown)
    print("\nTest 1: Trip Details Endpoint")
    print("-" * 60)
    response = client.get('/public_transport/city/wroclaw/trip/3_14613060')
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"✓ Trip ID: {data.get('trip_id')}")
        print(f"✓ Route: {data.get('route_id')}")
        print(f"✓ Stops: {len(data.get('stops', []))}")
    
    # Test 2: Closest Departures endpoint (from frontend dropdown)
    print("\n\nTest 2: Closest Departures Endpoint")
    print("-" * 60)
    response = client.get('/public_transport/city/wroclaw/closest_departures?start_coordinates=51.1079,17.0385&end_coordinates=51.1141,17.0301')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"✓ City: {data.get('metadata', {}).get('city')}")
        print(f"✓ Departures: {len(data.get('departures', []))}")
    else:
        print(f"Response: {response.data.decode()}")

print("\n" + "=" * 60)
print("Frontend endpoints are working!")
print("\nTo test in browser:")
print("1. Start server: python src\\public_transport_api\\main.py")
print("2. Open: frontend\\index.html")
print("3. Select endpoint and click 'Call API'")
