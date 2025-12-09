import sqlite3
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two coordinates"""
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def get_closest_departures(start_coordinates, end_coordinates, start_time, limit=5):
    conn = None
    try:
        start_lat, start_lon = map(float, start_coordinates.split(','))
        end_lat, end_lon = map(float, end_coordinates.split(','))
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        start_time_str = start_dt.strftime('%H:%M:%S')
        
        conn = sqlite3.connect("trips.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT
                t.trip_id,
                t.route_id,
                t.trip_headsign,
                s.stop_id,
                s.stop_name,
                s.stop_lat,
                s.stop_lon,
                st.arrival_time,
                st.departure_time
            FROM stops s
            JOIN stop_times st ON s.stop_id = st.stop_id
            JOIN trips t ON st.trip_id = t.trip_id
            WHERE st.departure_time >= ?
            ORDER BY st.departure_time
            LIMIT 100
        """
        
        cursor.execute(query, (start_time_str,))
        rows = cursor.fetchall()
        
        departures = []
        for row in rows:
            stop_lat = float(row['stop_lat'])
            stop_lon = float(row['stop_lon'])
            
            dist_to_start = haversine_distance(start_lat, start_lon, stop_lat, stop_lon)
            dist_to_end = haversine_distance(stop_lat, stop_lon, end_lat, end_lon)
            
            if dist_to_start <= 1000:
                departure = {
                    "trip_id": row['trip_id'],
                    "route_id": row['route_id'],
                    "trip_headsign": row['trip_headsign'],
                    "stop": {
                        "name": row['stop_name'],
                        "coordinates": {
                            "latitude": stop_lat,
                            "longitude": stop_lon
                        },
                        "arrival_time": f"{start_dt.date()}T{row['arrival_time']}Z",
                        "departure_time": f"{start_dt.date()}T{row['departure_time']}Z"
                    },
                    "distance_to_start": dist_to_start
                }
                departures.append(departure)
        
        departures.sort(key=lambda x: x['distance_to_start'])
        return departures[:limit]

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            conn.close()
