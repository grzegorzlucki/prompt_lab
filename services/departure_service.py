import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.geo_utils import calculate_distance, filter_stops_by_radius
from services.direction_service import is_heading_towards_destination

class DepartureService:
    """Service for querying public transport departures."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize service with database connection.
        
        Args:
            db_connection: SQLite database connection
        """
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
        """Get closest departures heading towards destination.
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Destination latitude
            end_lon: Destination longitude
            start_time: Departure time
            limit: Maximum number of results
            radius: Search radius in meters
            
        Returns:
            List of departure dictionaries
            
        Raises:
            ValueError: If coordinates are invalid
            sqlite3.Error: If database query fails
        """
        if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
            raise ValueError("Invalid start coordinates")
        if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
            raise ValueError("Invalid end coordinates")
        
        try:
            # Get all stops
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM stops")
            all_stops = [dict(row) for row in cursor.fetchall()]
            
            # Filter stops by radius
            nearby_stops = filter_stops_by_radius(start_lat, start_lon, all_stops, radius)
            
            if not nearby_stops:
                return []
            
            stop_ids = [s['stop_id'] for s in nearby_stops]
            stop_map = {s['stop_id']: s for s in nearby_stops}
            
            # Get departures for nearby stops
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
            
            # Group by trip_id
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
            
            # Filter and build departures
            departures = []
            start_time_str = start_time.strftime('%H:%M:%S')
            
            for trip_id, trip_data in trips.items():
                # Check direction
                if not is_heading_towards_destination(start_lat, start_lon, end_lat, end_lon, trip_data['stops']):
                    continue
                
                # Find departures after start_time
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
            
            # Sort by distance and limit
            departures.sort(key=lambda d: d['distance'])
            result = departures[:limit]
            
            # Remove distance from final output
            for d in result:
                del d['distance']
            
            return result
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database query failed: {e}")
    
    def _convert_to_iso(self, base_date: datetime, time_str: str) -> str:
        """Convert HH:MM:SS to ISO 8601 format.
        
        Args:
            base_date: Base date for conversion
            time_str: Time string in HH:MM:SS format
            
        Returns:
            ISO 8601 formatted datetime string
        """
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        
        # Handle times >= 24:00:00
        days_offset = hours // 24
        hours = hours % 24
        
        dt = base_date.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
        dt += timedelta(days=days_offset)
        
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
