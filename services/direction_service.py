import math
from typing import List, Dict, Any

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing (direction) in degrees from point 1 to point 2.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Bearing in degrees (0-360), where 0 is North, 90 is East, 180 is South, 270 is West
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    bearing = math.atan2(x, y)
    bearing_degrees = (math.degrees(bearing) + 360) % 360
    
    return bearing_degrees

def is_heading_towards_destination(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    trip_stops: List[Dict[str, Any]]
) -> bool:
    """Determine if a trip is heading towards the destination.
    
    Analyzes the trip's direction by comparing the bearing from start to destination
    with the general direction of the trip (from first to last stop).
    
    Args:
        start_lat: Starting point latitude
        start_lon: Starting point longitude
        end_lat: Destination latitude
        end_lon: Destination longitude
        trip_stops: List of stops with 'stop_lat' and 'stop_lon' keys, ordered by sequence
        
    Returns:
        True if trip is heading in the correct general direction, False otherwise
    """
    if not trip_stops or len(trip_stops) < 2:
        return True
    
    # Calculate desired bearing (start to destination)
    desired_bearing = calculate_bearing(start_lat, start_lon, end_lat, end_lon)
    
    # Calculate trip bearing (first stop to last stop)
    first_stop = trip_stops[0]
    last_stop = trip_stops[-1]
    trip_bearing = calculate_bearing(
        float(first_stop['stop_lat']),
        float(first_stop['stop_lon']),
        float(last_stop['stop_lat']),
        float(last_stop['stop_lon'])
    )
    
    # Calculate angular difference
    angle_diff = abs(desired_bearing - trip_bearing)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    # Accept if within 90 degrees (not opposite direction)
    return angle_diff <= 90
