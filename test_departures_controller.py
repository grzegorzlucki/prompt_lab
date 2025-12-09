import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from flask import Flask
from controllers.departures_controller import departures_bp

# Create test app
app = Flask(__name__)
app.register_blueprint(departures_bp)
app.config['TESTING'] = True

print("Testing DeparturesController:")
print("=" * 60)

with app.test_client() as client:
    
    # Test 1: Valid request
    print("\nTest 1: Valid request")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=51.1079,17.0385&'
        'end_coordinates=51.1141,17.0301&'
        'start_time=2025-04-02T08:30:00Z&'
        'limit=3'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Departures found: {len(data['departures'])}")
        print(f"Metadata city: {data['metadata']['city']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: {response.data}")
    
    # Test 2: Invalid city
    print("\n\nTest 2: Invalid city")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/warsaw/closest_departures?'
        'start_coordinates=51.1079,17.0385&'
        'end_coordinates=51.1141,17.0301'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✓ Test passed: City not supported")
    else:
        print(f"✗ Test failed: Expected 404, got {response.status_code}")
    
    # Test 3: Missing required parameter
    print("\n\nTest 3: Missing required parameter")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=51.1079,17.0385'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = json.loads(response.data)
        print(f"Error: {data['error']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: Expected 400, got {response.status_code}")
    
    # Test 4: Invalid coordinate format
    print("\n\nTest 4: Invalid coordinate format")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=invalid&'
        'end_coordinates=51.1141,17.0301'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = json.loads(response.data)
        print(f"Error: {data['error']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: Expected 400, got {response.status_code}")
    
    # Test 5: Invalid start_time format
    print("\n\nTest 5: Invalid start_time format")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=51.1079,17.0385&'
        'end_coordinates=51.1141,17.0301&'
        'start_time=invalid-time'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = json.loads(response.data)
        print(f"Error: {data['error']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: Expected 400, got {response.status_code}")
    
    # Test 6: Invalid limit
    print("\n\nTest 6: Invalid limit")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=51.1079,17.0385&'
        'end_coordinates=51.1141,17.0301&'
        'limit=-5'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = json.loads(response.data)
        print(f"Error: {data['error']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: Expected 400, got {response.status_code}")
    
    # Test 7: Default parameters
    print("\n\nTest 7: Default parameters (no start_time, default limit)")
    print("-" * 60)
    response = client.get(
        '/public_transport/city/wroclaw/closest_departures?'
        'start_coordinates=51.1079,17.0385&'
        'end_coordinates=51.1141,17.0301'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Departures found: {len(data['departures'])}")
        print(f"Default limit used: {data['metadata']['query_parameters']['limit']}")
        print("✓ Test passed")
    else:
        print(f"✗ Test failed: {response.data}")

print("\n" + "=" * 60)
print("All tests completed!")
