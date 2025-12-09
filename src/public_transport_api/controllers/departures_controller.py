from flask import Blueprint, jsonify, request
from datetime import datetime

from public_transport_api.services.departures_service import get_closest_departures

departures_bp = Blueprint('departures', __name__, url_prefix='/public_transport/city/<string:city>/closest_departures')

@departures_bp.route("/", methods=["GET"])
def closest_departures(city):
    """
    The endpoint returns the closest departures of lines that bring the user closer to the destination.
	Lines that start in the opposite direction shall not be displayed.
	Departures are sorted by distance from start_coordinates in ascend-ing order (the closest first).
	The endpoint does not consider which line brings the user closer to the destination.

    Request Parameters:
        Path Parameters:
        - city (required): The city for the public transport search. Currently, on-ly "wroclaw" is supported.
        Query Parameters:
        - start_coordinates (required): The geolocation coordinates where the user wants to start the trip.
        - end_coordinates (required): The geolocation coordinates where the user wants to finish the trip.
        - start_time (optional, default: current time): The time at which the us-er starts the trip.
        - limit (optional, default: 5): The maximum number of departures to be returned.
    """
    if city.lower() != 'wroclaw':
        return jsonify({"error": "City not supported"}), 404
    
    start_coords = request.args.get('start_coordinates')
    end_coords = request.args.get('end_coordinates')
    
    if not start_coords or not end_coords:
        return jsonify({"error": "start_coordinates and end_coordinates are required"}), 400
    
    start_time = request.args.get('start_time', datetime.now().isoformat())
    limit = int(request.args.get('limit', 5))
    
    departures = get_closest_departures(start_coords, end_coords, start_time, limit)
    return jsonify({"departures": departures})