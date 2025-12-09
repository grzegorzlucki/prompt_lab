// Global map variable (assumes Leaflet.js is loaded)
let map;
let markersLayer;

/**
 * Fetches closest departures from the API
 */
async function fetchClosestDepartures(startCoords, endCoords, startTime, limit = 10) {
    const statusEl = document.getElementById('status-message');
    const outputEl = document.getElementById('json-output');
    
    try {
        statusEl.textContent = 'Loading...';
        statusEl.className = 'mt-4 text-center text-sm text-blue-600';
        
        const params = new URLSearchParams({
            start_coordinates: `${startCoords.lat},${startCoords.lon}`,
            end_coordinates: `${endCoords.lat},${endCoords.lon}`,
            start_time: startTime,
            limit: limit
        });
        
        const response = await fetch(`http://localhost:5001/public_transport/city/Wroclaw/closest_departures?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display raw JSON
        outputEl.value = JSON.stringify(data, null, 2);
        
        // Display formatted results
        displayResults(data.departures || []);
        
        // Add markers to map
        if (typeof L !== 'undefined' && map) {
            addStopMarkers(data.departures || []);
        }
        
        statusEl.textContent = `Found ${data.departures?.length || 0} departures`;
        statusEl.className = 'mt-4 text-center text-sm text-green-600';
        
        return data;
        
    } catch (error) {
        showError(error.message);
        throw error;
    }
}

/**
 * Displays departure results in a user-friendly format
 */
function displayResults(departures) {
    let resultsContainer = document.getElementById('results-container');
    
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'results-container';
        resultsContainer.className = 'mt-6';
        document.querySelector('.bg-white').appendChild(resultsContainer);
    }
    
    if (!departures || departures.length === 0) {
        resultsContainer.innerHTML = '<p class="text-center text-gray-500">No departures found</p>';
        return;
    }
    
    resultsContainer.innerHTML = `
        <h2 class="text-xl font-bold text-gray-800 mb-4">Departures</h2>
        <div class="space-y-3">
            ${departures.map(dep => `
                <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h3 class="font-bold text-lg text-gray-800">${dep.stop?.name || 'Unknown Stop'}</h3>
                            <p class="text-sm text-gray-600">Route: <span class="font-semibold">${dep.route_id || 'N/A'}</span></p>
                            <p class="text-sm text-gray-600">To: <span class="font-semibold">${dep.trip_headsign || 'N/A'}</span></p>
                        </div>
                        <div class="text-right">
                            <p class="text-lg font-bold text-blue-600">${formatTime(dep.stop?.departure_time)}</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Adds markers to the map for each departure stop
 */
function addStopMarkers(departures) {
    if (!map || !departures || departures.length === 0) return;
    
    // Clear existing markers
    if (markersLayer) {
        markersLayer.clearLayers();
    } else {
        markersLayer = L.layerGroup().addTo(map);
    }
    
    departures.forEach(dep => {
        if (dep.stop?.coordinates?.latitude && dep.stop?.coordinates?.longitude) {
            const marker = L.marker([dep.stop.coordinates.latitude, dep.stop.coordinates.longitude])
                .bindPopup(`
                    <div class="p-2">
                        <h3 class="font-bold">${dep.stop?.name || 'Unknown Stop'}</h3>
                        <p><strong>Route:</strong> ${dep.route_id || 'N/A'}</p>
                        <p><strong>To:</strong> ${dep.trip_headsign || 'N/A'}</p>
                        <p><strong>Departure:</strong> ${formatTime(dep.stop?.departure_time)}</p>
                    </div>
                `);
            
            markersLayer.addLayer(marker);
        }
    });
    
    // Fit map to show all markers
    if (markersLayer.getLayers().length > 0) {
        map.fitBounds(markersLayer.getBounds(), { padding: [50, 50] });
    }
}

/**
 * Formats ISO time string to readable format
 */
function formatTime(isoString) {
    if (!isoString) return 'N/A';
    
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
    } catch (error) {
        return isoString;
    }
}

/**
 * Shows error message to user
 */
function showError(message) {
    const statusEl = document.getElementById('status-message');
    const outputEl = document.getElementById('json-output');
    
    statusEl.textContent = `Error: ${message}`;
    statusEl.className = 'mt-4 text-center text-sm text-red-600';
    
    outputEl.value = `Error: ${message}`;
    
    // Clear results
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        resultsContainer.innerHTML = '<p class="text-center text-red-500">Failed to load departures</p>';
    }
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchClosestDepartures,
        displayResults,
        addStopMarkers,
        formatTime,
        showError
    };
}
