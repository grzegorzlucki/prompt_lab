import math
from typing import List, Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two GPS coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def filter_stops_by_radius(start_lat: float, start_lon: float, stops: List[Dict[str, Any]], radius: float = 1000) -> List[Dict[str, Any]]:
    """Filter stops within a given radius from start coordinates.
    
    Args:
        start_lat: Starting latitude
        start_lon: Starting longitude
        stops: List of stop dictionaries with 'stop_lat' and 'stop_lon' keys
        radius: Maximum distance in meters (default: 1000)
        
    Returns:
        List of stops within radius, each with added 'distance' key
    """
    filtered = []
    for stop in stops:
        distance = calculate_distance(start_lat, start_lon, float(stop['stop_lat']), float(stop['stop_lon']))
        if distance <= radius:
            stop['distance'] = distance
            filtered.append(stop)
    return sorted(filtered, key=lambda s: s['distance'])
