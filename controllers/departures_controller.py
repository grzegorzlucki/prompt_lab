from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Tuple, Dict, Any
import sqlite3
from services.departure_service import DepartureService

departures_bp = Blueprint('departures', __name__)

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect('wroclaw_transport.db')
    return conn

@departures_bp.route('/public_transport/city/<city>/closest_departures', methods=['GET'])
def get_closest_departures(city: str) -> Tuple[Dict[str, Any], int]:
    """Get closest departures heading towards destination.
    
    Args:
        city: City name (path parameter)
        
    Query Parameters:
        start_coordinates: Starting coordinates as "lat,lon"
        end_coordinates: Destination coordinates as "lat,lon"
        start_time: ISO 8601 datetime (optional, defaults to now)
        limit: Maximum results (optional, default 5)
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    # Validate city
    if city.lower() != 'wroclaw':
        return jsonify({'error': 'City not supported'}), 404
    
    try:
        # Get query parameters
        start_coords_str = request.args.get('start_coordinates')
        end_coords_str = request.args.get('end_coordinates')
        start_time_str = request.args.get('start_time')
        limit_str = request.args.get('limit', '5')
        
        # Validate required parameters
        if not start_coords_str:
            return jsonify({'error': 'Missing required parameter: start_coordinates'}), 400
        if not end_coords_str:
            return jsonify({'error': 'Missing required parameter: end_coordinates'}), 400
        
        # Parse coordinates
        try:
            start_lat, start_lon = map(float, start_coords_str.split(','))
            end_lat, end_lon = map(float, end_coords_str.split(','))
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid coordinate format. Expected: "lat,lon"'}), 400
        
        # Parse start_time
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid start_time format. Expected ISO 8601'}), 400
        else:
            start_time = datetime.now()
        
        # Parse limit
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid limit. Expected positive integer'}), 400
        
        # Get departures
        conn = get_db_connection()
        try:
            service = DepartureService(conn)
            departures = service.get_closest_departures(
                start_lat, start_lon,
                end_lat, end_lon,
                start_time,
                limit
            )
        finally:
            conn.close()
        
        # Build response
        response = {
            'metadata': {
                'self': request.full_path.rstrip('?'),
                'city': city,
                'query_parameters': {
                    'start_coordinates': start_coords_str,
                    'end_coordinates': end_coords_str,
                    'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'limit': limit
                }
            },
            'departures': departures
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
