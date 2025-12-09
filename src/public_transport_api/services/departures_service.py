import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
from utils.geo_utils import calculate_distance, filter_stops_by_radius
from src.public_transport_api.services.direction_service import is_heading_towards_destination

class DepartureService:
    """Service for querying public transport departures."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
        self.db.row_factory = sqlite3.Row
    
    def get_closest_departures(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        start_time: datetime,
        limit: int = 5,
        radius: float = 1000
    ) -> List[Dict[str, Any]]:
        if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
            raise ValueError("Invalid start coordinates")
        if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
            raise ValueError("Invalid end coordinates")
        
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM stops")
            all_stops = [dict(row) for row in cursor.fetchall()]
            
            nearby_stops = filter_stops_by_radius(start_lat, start_lon, all_stops, radius)
            
            if not nearby_stops:
                return []
            
            stop_ids = [s['stop_id'] for s in nearby_stops]
            stop_map = {s['stop_id']: s for s in nearby_stops}
            
            placeholders = ','.join('?' * len(stop_ids))
            query = f"""
                SELECT st.trip_id, st.stop_id, st.arrival_time, st.departure_time, st.stop_sequence,
                       t.route_id, t.trip_headsign,
                       s.stop_name, s.stop_lat, s.stop_lon
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                JOIN stops s ON st.stop_id = s.stop_id
                WHERE st.stop_id IN ({placeholders})
                ORDER BY st.trip_id, st.stop_sequence
            """
            
            cursor.execute(query, stop_ids)
            rows = cursor.fetchall()
            
            trips = {}
            for row in rows:
                trip_id = row['trip_id']
                if trip_id not in trips:
                    trips[trip_id] = {
                        'route_id': row['route_id'],
                        'trip_headsign': row['trip_headsign'],
                        'stops': []
                    }
                trips[trip_id]['stops'].append(dict(row))
            
            departures = []
            start_time_str = start_time.strftime('%H:%M:%S')
            
            for trip_id, trip_data in trips.items():
                if not is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_data['stops']):
                    continue
                
                for stop in trip_data['stops']:
                    if stop['stop_id'] not in stop_map:
                        continue
                    
                    if stop['departure_time'] >= start_time_str:
                        departures.append({
                            'trip_id': trip_id,
                            'route_id': trip_data['route_id'],
                            'trip_headsign': trip_data['trip_headsign'],
                            'stop': {
                                'name': stop['stop_name'],
                                'coordinates': {
                                    'latitude': float(stop['stop_lat']),
                                    'longitude': float(stop['stop_lon'])
                                },
                                'arrival_time': self._convert_to_iso(start_time, stop['arrival_time']),
                                'departure_time': self._convert_to_iso(start_time, stop['departure_time'])
                            },
                            'distance': stop_map[stop['stop_id']]['distance']
                        })
                        break
            
            departures.sort(key=lambda d: d['distance'])
            result = departures[:limit]
            
            for d in result:
                del d['distance']
            
            return result
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database query failed: {e}")
    
    def _convert_to_iso(self, base_date: datetime, time_str: str) -> str:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        
        days_offset = hours // 24
        hours = hours % 24
        
        dt = base_date.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
        dt += timedelta(days=days_offset)
        
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
