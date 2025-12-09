// Initialize controls when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeControls);

/**
 * Initialize all controls and event listeners
 */
function initializeControls() {
    setDefaultDateTime();
    
    const findBtn = document.getElementById('find-departures-btn');
    findBtn.addEventListener('click', handleFindDepartures);
    
    // Toggle JSON output
    const toggleBtn = document.getElementById('toggle-json');
    const jsonOutput = document.getElementById('json-output');
    toggleBtn.addEventListener('click', () => {
        jsonOutput.classList.toggle('hidden');
        toggleBtn.textContent = jsonOutput.classList.contains('hidden') 
            ? '▼ Show Raw JSON Response' 
            : '▲ Hide Raw JSON Response';
    });
}

/**
 * Set default date/time to current time
 */
function setDefaultDateTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('departure-time').value = now.toISOString().slice(0, 16);
}

/**
 * Validate all inputs before API call
 */
function validateInputs() {
    let isValid = true;
    
    // Clear previous errors
    document.querySelectorAll('[id$="-error"]').forEach(el => el.textContent = '');
    
    const startLat = parseFloat(document.getElementById('start-lat').value);
    const startLon = parseFloat(document.getElementById('start-lon').value);
    const endLat = parseFloat(document.getElementById('end-lat').value);
    const endLon = parseFloat(document.getElementById('end-lon').value);
    const departureTime = document.getElementById('departure-time').value;
    const limit = parseInt(document.getElementById('result-limit').value);
    
    // Validate start coordinates
    if (isNaN(startLat) || startLat < -90 || startLat > 90) {
        showValidationError('start-lat', 'Invalid latitude (-90 to 90)');
        isValid = false;
    }
    if (isNaN(startLon) || startLon < -180 || startLon > 180) {
        showValidationError('start-lon', 'Invalid longitude (-180 to 180)');
        isValid = false;
    }
    
    // Validate end coordinates
    if (isNaN(endLat) || endLat < -90 || endLat > 90) {
        showValidationError('end-lat', 'Invalid latitude (-90 to 90)');
        isValid = false;
    }
    if (isNaN(endLon) || endLon < -180 || endLon > 180) {
        showValidationError('end-lon', 'Invalid longitude (-180 to 180)');
        isValid = false;
    }
    
    // Validate departure time
    if (!departureTime) {
        showValidationError('departure-time', 'Departure time is required');
        isValid = false;
    }
    
    // Validate limit
    if (isNaN(limit) || limit < 1 || limit > 20) {
        showValidationError('result-limit', 'Limit must be between 1 and 20');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show validation error for a specific field
 */
function showValidationError(field, message) {
    const errorEl = document.getElementById(`${field}-error`);
    if (errorEl) {
        errorEl.textContent = message;
    }
    
    const inputEl = document.getElementById(field);
    if (inputEl) {
        inputEl.classList.add('border-red-500');
        setTimeout(() => inputEl.classList.remove('border-red-500'), 3000);
    }
}

/**
 * Handle Find Departures button click
 */
async function handleFindDepartures() {
    if (!validateInputs()) {
        return;
    }
    
    const btn = document.getElementById('find-departures-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('loading-spinner');
    
    // Disable button and show spinner
    btn.disabled = true;
    btn.classList.add('opacity-75', 'cursor-not-allowed');
    btnText.textContent = 'Loading...';
    spinner.classList.remove('hidden');
    
    try {
        const startCoords = {
            lat: parseFloat(document.getElementById('start-lat').value),
            lon: parseFloat(document.getElementById('start-lon').value)
        };
        
        const endCoords = {
            lat: parseFloat(document.getElementById('end-lat').value),
            lon: parseFloat(document.getElementById('end-lon').value)
        };
        
        const departureTime = document.getElementById('departure-time').value;
        const limit = parseInt(document.getElementById('result-limit').value);
        
        // Convert datetime-local to ISO format
        const isoTime = new Date(departureTime).toISOString();
        
        await fetchClosestDepartures(startCoords, endCoords, isoTime, limit);
        
    } catch (error) {
        console.error('Error fetching departures:', error);
    } finally {
        // Re-enable button and hide spinner
        btn.disabled = false;
        btn.classList.remove('opacity-75', 'cursor-not-allowed');
        btnText.textContent = 'Find Departures';
        spinner.classList.add('hidden');
    }
}
