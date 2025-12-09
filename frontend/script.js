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

function searchDepartures() {
    if (!startCoords || !endCoords) {
        displayStatus('Please select both start and destination points on the map', 'text-red-600');
        return;
    }
    
    displayStatus('Searching for departures...', 'text-blue-600');
    // API call will be implemented in next step
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
