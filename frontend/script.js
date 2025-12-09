let map;
let startMarker = null;
let endMarker = null;
let startCoords = null;
let endCoords = null;

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initControls();
});

function initControls() {
    // Set departure time to current time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('departure-time').value = now.toISOString().slice(0, 16);
    
    // Add search button handler
    document.getElementById('search-btn').addEventListener('click', searchDepartures);
}

async function searchDepartures() {
    if (!startCoords || !endCoords) {
        displayStatus('Please select both start and destination points on the map', 'text-red-600');
        return;
    }
    
    const departureTime = document.getElementById('departure-time').value;
    const limit = document.getElementById('limit').value;
    
    // Convert datetime-local to ISO 8601 format
    const startTime = new Date(departureTime).toISOString();
    
    // Build query parameters
    const params = new URLSearchParams({
        start_coordinates: `${startCoords.lat},${startCoords.lng}`,
        end_coordinates: `${endCoords.lat},${endCoords.lng}`,
        start_time: startTime,
        limit: limit
    });
    
    const apiUrl = `http://localhost:5001/public_transport/city/wroclaw/closest_departures?${params}`;
    
    displayStatus('Searching for departures...', 'text-blue-600');
    document.getElementById('search-btn').disabled = true;
    
    try {
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.departures && data.departures.length > 0) {
            displayStatus(`Found ${data.departures.length} departure(s)`, 'text-green-600');
            displayDepartures(data.departures);
        } else {
            displayStatus('No departures found', 'text-yellow-600');
        }
        
    } catch (error) {
        console.error('API Error:', error);
        displayStatus(`Error: ${error.message}`, 'text-red-600');
    } finally {
        document.getElementById('search-btn').disabled = false;
    }
}

let departureMarkers = [];

function displayDepartures(departures) {
    // Clear previous markers
    departureMarkers.forEach(marker => map.removeLayer(marker));
    departureMarkers = [];
    
    departures.forEach(departure => {
        const lat = departure.stop.coordinates.latitude;
        const lng = departure.stop.coordinates.longitude;
        
        const marker = L.marker([lat, lng], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            })
        }).addTo(map);
        
        const popupContent = `
            <div class="font-sans">
                <h3 class="font-bold text-lg">${departure.stop.name}</h3>
                <p><strong>Line:</strong> ${departure.route_id}</p>
                <p><strong>Direction:</strong> ${departure.trip_headsign}</p>
                <p><strong>Departure:</strong> ${new Date(departure.stop.departure_time).toLocaleTimeString()}</p>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        departureMarkers.push(marker);
    });
}

function displayStatus(message, colorClass) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = `text-center text-sm font-semibold ${colorClass}`;
}

function initMap() {
    // Initialize map centered on Wrocław
    map = L.map('map').setView([51.1079, 17.0385], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Handle map clicks
    map.on('click', handleMapClick);
}

function handleMapClick(e) {
    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);
    
    if (!startCoords) {
        // Set start point
        startCoords = { lat, lng };
        document.getElementById('start-coords').value = `${lat}, ${lng}`;
        
        if (startMarker) map.removeLayer(startMarker);
        startMarker = L.marker([lat, lng], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41]
            })
        }).addTo(map).bindPopup('Start').openPopup();
        
    } else if (!endCoords) {
        // Set destination point
        endCoords = { lat, lng };
        document.getElementById('end-coords').value = `${lat}, ${lng}`;
        
        if (endMarker) map.removeLayer(endMarker);
        endMarker = L.marker([lat, lng], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41]
            })
        }).addTo(map).bindPopup('Destination').openPopup();
        
    } else {
        // Reset and start over
        startCoords = { lat, lng };
        endCoords = null;
        document.getElementById('start-coords').value = `${lat}, ${lng}`;
        document.getElementById('end-coords').value = '';
        
        if (startMarker) map.removeLayer(startMarker);
        if (endMarker) map.removeLayer(endMarker);
        
        startMarker = L.marker([lat, lng], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41]
            })
        }).addTo(map).bindPopup('Start').openPopup();
        
        displayStatus('Now click to set destination', 'text-blue-600');
    }
}
