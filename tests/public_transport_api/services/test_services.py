import pytest
import sqlite3
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from src.public_transport_api.services.departures_service import DepartureService
from src.public_transport_api.services import trips_service


@pytest.fixture
def mock_db():
    """Mock database connection."""
    db = Mock(spec=sqlite3.Connection)
    db.row_factory = sqlite3.Row
    return db


@pytest.fixture
def mock_cursor():
    """Mock database cursor."""
    cursor = Mock()
    return cursor


@pytest.fixture
def sample_stops():
    """Sample stop data."""
    return [
        {'stop_id': 'S1', 'stop_name': 'Stop A', 'stop_lat': 51.1079, 'stop_lon': 17.0385},
        {'stop_id': 'S2', 'stop_name': 'Stop B', 'stop_lat': 51.1100, 'stop_lon': 17.0400},
        {'stop_id': 'S3', 'stop_name': 'Stop C', 'stop_lat': 51.2000, 'stop_lon': 17.2000}
    ]


@pytest.fixture
def sample_stop_times():
    """Sample stop times data."""
    return [
        {'trip_id': 'T1', 'stop_id': 'S1', 'arrival_time': '08:00:00', 'departure_time': '08:01:00',
         'stop_sequence': 1, 'route_id': 'R1', 'trip_headsign': 'Downtown',
         'stop_name': 'Stop A', 'stop_lat': 51.1079, 'stop_lon': 17.0385},
        {'trip_id': 'T1', 'stop_id': 'S2', 'arrival_time': '08:10:00', 'departure_time': '08:11:00',
         'stop_sequence': 2, 'route_id': 'R1', 'trip_headsign': 'Downtown',
         'stop_name': 'Stop B', 'stop_lat': 51.1100, 'stop_lon': 17.0400}
    ]


@pytest.fixture
def departure_service(mock_db):
    """Create DepartureService instance with mock database."""
    return DepartureService(mock_db)


class TestDepartureService:
    """Tests for DepartureService."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = DepartureService(mock_db)
        assert service.db == mock_db
        assert mock_db.row_factory == sqlite3.Row

    def test_get_closest_departures_valid_inputs(self, departure_service, mock_db, mock_cursor, sample_stops, sample_stop_times):
        """Test finding departures with valid inputs."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            [create_row_mock(st) for st in sample_stop_times]
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter, \
             patch('src.public_transport_api.services.departures_service.is_heading_towards_destination') as mock_heading:
            
            mock_filter.return_value = [
                {**sample_stops[0], 'distance': 100},
                {**sample_stops[1], 'distance': 200}
            ]
            mock_heading.return_value = True
            
            result = departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 7, 0, 0),
                limit=5,
                radius=1000
            )
            
            assert isinstance(result, list)
            assert len(result) <= 5
            mock_filter.assert_called_once()
            mock_heading.assert_called()

    def test_get_closest_departures_invalid_start_coordinates(self, departure_service):
        """Test with invalid start coordinates."""
        with pytest.raises(ValueError, match="Invalid start coordinates"):
            departure_service.get_closest_departures(
                start_lat=91.0,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )

    def test_get_closest_departures_invalid_end_coordinates(self, departure_service):
        """Test with invalid end coordinates."""
        with pytest.raises(ValueError, match="Invalid end coordinates"):
            departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=181.0,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )

    def test_filtering_by_radius(self, departure_service, mock_db, mock_cursor, sample_stops):
        """Test filtering by radius."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            []
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter:
            mock_filter.return_value = [{**sample_stops[0], 'distance': 100}]
            
            departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0),
                radius=500
            )
            
            mock_filter.assert_called_once_with(51.1079, 17.0385, sample_stops, 500)

    def test_direction_filtering(self, departure_service, mock_db, mock_cursor, sample_stops, sample_stop_times):
        """Test direction filtering."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            [create_row_mock(st) for st in sample_stop_times]
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter, \
             patch('src.public_transport_api.services.departures_service.is_heading_towards_destination') as mock_heading:
            
            mock_filter.return_value = [{**sample_stops[0], 'distance': 100}]
            mock_heading.return_value = False
            
            result = departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )
            
            assert result == []

    def test_time_filtering(self, departure_service, mock_db, mock_cursor, sample_stops, sample_stop_times):
        """Test time filtering."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        past_stop_times = [
            {**sample_stop_times[0], 'departure_time': '06:00:00'}
        ]
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            [create_row_mock(st) for st in past_stop_times]
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter, \
             patch('src.public_transport_api.services.departures_service.is_heading_towards_destination') as mock_heading:
            
            mock_filter.return_value = [{**sample_stops[0], 'distance': 100}]
            mock_heading.return_value = True
            
            result = departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )
            
            assert result == []

    def test_limit_parameter(self, departure_service, mock_db, mock_cursor, sample_stops):
        """Test limit parameter."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        many_stop_times = []
        for i in range(10):
            many_stop_times.append({
                'trip_id': f'T{i}', 'stop_id': 'S1', 'arrival_time': f'08:{i:02d}:00',
                'departure_time': f'08:{i:02d}:00', 'stop_sequence': 1, 'route_id': 'R1',
                'trip_headsign': 'Downtown', 'stop_name': 'Stop A',
                'stop_lat': 51.1079, 'stop_lon': 17.0385
            })
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            [create_row_mock(st) for st in many_stop_times]
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter, \
             patch('src.public_transport_api.services.departures_service.is_heading_towards_destination') as mock_heading:
            
            mock_filter.return_value = [{**sample_stops[0], 'distance': 100}]
            mock_heading.return_value = True
            
            result = departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 7, 0, 0),
                limit=3
            )
            
            assert len(result) <= 3

    def test_no_results(self, departure_service, mock_db, mock_cursor, sample_stops):
        """Test with no results."""
        mock_db.cursor.return_value = mock_cursor
        
        def create_row_mock(data):
            m = Mock()
            m.keys.return_value = data.keys()
            m.__getitem__ = lambda self, key: data[key]
            return m
        
        mock_cursor.fetchall.side_effect = [
            [create_row_mock(stop) for stop in sample_stops],
            []
        ]
        
        with patch('src.public_transport_api.services.departures_service.filter_stops_by_radius') as mock_filter:
            mock_filter.return_value = []
            
            result = departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )
            
            assert result == []

    def test_database_error(self, departure_service, mock_db, mock_cursor):
        """Test database error handling."""
        mock_db.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = sqlite3.Error("Database error")
        
        with pytest.raises(sqlite3.Error, match="Database query failed"):
            departure_service.get_closest_departures(
                start_lat=51.1079,
                start_lon=17.0385,
                end_lat=51.1100,
                end_lon=17.0400,
                start_time=datetime(2025, 4, 2, 8, 0, 0)
            )

    def test_convert_to_iso_normal_time(self, departure_service):
        """Test ISO time conversion for normal time."""
        base_date = datetime(2025, 4, 2, 0, 0, 0)
        result = departure_service._convert_to_iso(base_date, '08:30:45')
        assert result == '2025-04-02T08:30:45Z'

    def test_convert_to_iso_overflow_time(self, departure_service):
        """Test ISO time conversion for time overflow (>24h)."""
        base_date = datetime(2025, 4, 2, 0, 0, 0)
        result = departure_service._convert_to_iso(base_date, '25:30:00')
        assert result == '2025-04-03T01:30:00Z'


class TestTripService:
    """Tests for trip_service."""

    @patch('src.public_transport_api.services.trips_service.sqlite3.connect')
    def test_get_trip_details_valid_trip(self, mock_connect):
        """Test retrieving valid trip."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('R1', 'Downtown')
        
        result = trips_service.get_trip_details('T1')
        
        assert result is not None
        assert result['trip_id'] == 'T1'
        assert result['route_id'] == 'R1'
        assert result['trip_headsign'] == 'Downtown'
        assert 'stops' in result
        assert len(result['stops']) == 3

    @patch('src.public_transport_api.services.trips_service.sqlite3.connect')
    def test_get_trip_details_invalid_trip_id(self, mock_connect):
        """Test with invalid trip_id."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = trips_service.get_trip_details('INVALID')
        
        assert result is None

    @patch('src.public_transport_api.services.trips_service.sqlite3.connect')
    def test_get_trip_details_stop_ordering(self, mock_connect):
        """Test stop ordering in trip details."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('R1', 'Downtown')
        
        result = trips_service.get_trip_details('T1')
        
        assert result is not None
        stops = result['stops']
        assert len(stops) == 3
        assert stops[0]['name'] == 'Mock Stop A'
        assert stops[1]['name'] == 'Mock Stop B'
        assert stops[2]['name'] == 'Mock Stop C'
        
        for i in range(len(stops) - 1):
            assert stops[i]['departure_time'] < stops[i + 1]['arrival_time']
