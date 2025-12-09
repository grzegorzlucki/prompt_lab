describe('API Module (api.js)', () => {
    let originalFetch;
    
    beforeEach(() => {
        originalFetch = global.fetch;
        document.body.innerHTML = `
            <div id="status-message"></div>
            <textarea id="json-output"></textarea>
            <div id="results-container"></div>
        `;
        global.L = {
            marker: jasmine.createSpy('marker').and.returnValue({
                bindPopup: jasmine.createSpy('bindPopup').and.returnValue({})
            }),
            layerGroup: jasmine.createSpy('layerGroup').and.returnValue({
                addTo: jasmine.createSpy('addTo').and.returnValue({
                    clearLayers: jasmine.createSpy('clearLayers'),
                    addLayer: jasmine.createSpy('addLayer'),
                    getLayers: jasmine.createSpy('getLayers').and.returnValue([{}]),
                    getBounds: jasmine.createSpy('getBounds')
                })
            })
        };
        global.map = {
            fitBounds: jasmine.createSpy('fitBounds')
        };
    });
    
    afterEach(() => {
        global.fetch = originalFetch;
        delete global.L;
        delete global.map;
        delete global.markersLayer;
    });
    
    describe('fetchClosestDepartures', () => {
        it('should construct correct API URL with parameters', async () => {
            global.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ departures: [] })
            }));
            
            await fetchClosestDepartures(
                { lat: 51.1, lon: 17.0 },
                { lat: 51.2, lon: 17.1 },
                '2024-01-01T10:00:00Z',
                5
            );
            
            expect(global.fetch).toHaveBeenCalledWith(
                jasmine.stringContaining('start_lat=51.1')
            );
            expect(global.fetch).toHaveBeenCalledWith(
                jasmine.stringContaining('start_lon=17')
            );
            expect(global.fetch).toHaveBeenCalledWith(
                jasmine.stringContaining('end_lat=51.2')
            );
            expect(global.fetch).toHaveBeenCalledWith(
                jasmine.stringContaining('limit=5')
            );
        });
        
        it('should parse and return response data', async () => {
            const mockData = { departures: [{ stop_name: 'Test Stop' }] };
            global.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockData)
            }));
            
            const result = await fetchClosestDepartures(
                { lat: 51.1, lon: 17.0 },
                { lat: 51.2, lon: 17.1 },
                '2024-01-01T10:00:00Z'
            );
            
            expect(result).toEqual(mockData);
        });
        
        it('should handle HTTP errors', async () => {
            global.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve({
                ok: false,
                status: 404
            }));
            
            await expectAsync(
                fetchClosestDepartures(
                    { lat: 51.1, lon: 17.0 },
                    { lat: 51.2, lon: 17.1 },
                    '2024-01-01T10:00:00Z'
                )
            ).toBeRejected();
        });
        
        it('should handle network errors', async () => {
            global.fetch = jasmine.createSpy('fetch').and.returnValue(
                Promise.reject(new Error('Network error'))
            );
            
            await expectAsync(
                fetchClosestDepartures(
                    { lat: 51.1, lon: 17.0 },
                    { lat: 51.2, lon: 17.1 },
                    '2024-01-01T10:00:00Z'
                )
            ).toBeRejectedWithError('Network error');
        });
        
        it('should update status message on success', async () => {
            global.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ departures: [1, 2, 3] })
            }));
            
            await fetchClosestDepartures(
                { lat: 51.1, lon: 17.0 },
                { lat: 51.2, lon: 17.1 },
                '2024-01-01T10:00:00Z'
            );
            
            const statusEl = document.getElementById('status-message');
            expect(statusEl.textContent).toContain('Found 3 departures');
        });
    });
    
    describe('displayResults', () => {
        it('should display message when no departures', () => {
            displayResults([]);
            const container = document.getElementById('results-container');
            expect(container.innerHTML).toContain('No departures found');
        });
        
        it('should render departure cards', () => {
            const departures = [{
                stop_name: 'Main Station',
                route_id: '10',
                trip_headsign: 'City Center',
                departure_time: '2024-01-01T10:30:00Z'
            }];
            
            displayResults(departures);
            const container = document.getElementById('results-container');
            expect(container.innerHTML).toContain('Main Station');
            expect(container.innerHTML).toContain('10');
            expect(container.innerHTML).toContain('City Center');
        });
    });
    
    describe('formatTime', () => {
        it('should format ISO time string', () => {
            const result = formatTime('2024-01-01T14:30:00Z');
            expect(result).toMatch(/\d{2}:\d{2}/);
        });
        
        it('should handle invalid time', () => {
            const result = formatTime(null);
            expect(result).toBe('N/A');
        });
        
        it('should return original string on parse error', () => {
            const result = formatTime('invalid');
            expect(result).toBe('invalid');
        });
    });
    
    describe('showError', () => {
        it('should display error message', () => {
            showError('Test error');
            const statusEl = document.getElementById('status-message');
            expect(statusEl.textContent).toContain('Test error');
            expect(statusEl.className).toContain('text-red-600');
        });
        
        it('should update output textarea', () => {
            showError('API failed');
            const outputEl = document.getElementById('json-output');
            expect(outputEl.value).toContain('API failed');
        });
    });
    
    describe('addStopMarkers', () => {
        it('should add markers for each departure', () => {
            const departures = [
                { stop_lat: 51.1, stop_lon: 17.0, stop_name: 'Stop 1' },
                { stop_lat: 51.2, stop_lon: 17.1, stop_name: 'Stop 2' }
            ];
            
            addStopMarkers(departures);
            expect(global.L.marker).toHaveBeenCalledTimes(2);
        });
        
        it('should skip departures without coordinates', () => {
            const departures = [
                { stop_name: 'Stop 1' },
                { stop_lat: 51.1, stop_lon: 17.0, stop_name: 'Stop 2' }
            ];
            
            addStopMarkers(departures);
            expect(global.L.marker).toHaveBeenCalledTimes(1);
        });
    });
});

describe('Controls Module (controls.js)', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <input type="number" id="start-lat" />
            <span id="start-lat-error"></span>
            <input type="number" id="start-lon" />
            <span id="start-lon-error"></span>
            <input type="number" id="end-lat" />
            <span id="end-lat-error"></span>
            <input type="number" id="end-lon" />
            <span id="end-lon-error"></span>
            <input type="datetime-local" id="departure-time" />
            <span id="departure-time-error"></span>
            <input type="number" id="result-limit" value="5" />
            <span id="result-limit-error"></span>
            <button id="find-departures-btn">
                <span id="btn-text">Find</span>
                <svg id="loading-spinner" class="hidden"></svg>
            </button>
        `;
        global.fetchClosestDepartures = jasmine.createSpy('fetchClosestDepartures')
            .and.returnValue(Promise.resolve({}));
    });
    
    afterEach(() => {
        delete global.fetchClosestDepartures;
    });
    
    describe('setDefaultDateTime', () => {
        it('should set current datetime', () => {
            setDefaultDateTime();
            const input = document.getElementById('departure-time');
            expect(input.value).toBeTruthy();
            expect(input.value).toMatch(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/);
        });
    });
    
    describe('validateInputs', () => {
        it('should validate latitude range', () => {
            document.getElementById('start-lat').value = '100';
            document.getElementById('start-lon').value = '17';
            document.getElementById('end-lat').value = '51';
            document.getElementById('end-lon').value = '17';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            
            const result = validateInputs();
            expect(result).toBe(false);
            expect(document.getElementById('start-lat-error').textContent).toBeTruthy();
        });
        
        it('should validate longitude range', () => {
            document.getElementById('start-lat').value = '51';
            document.getElementById('start-lon').value = '200';
            document.getElementById('end-lat').value = '51';
            document.getElementById('end-lon').value = '17';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            
            const result = validateInputs();
            expect(result).toBe(false);
            expect(document.getElementById('start-lon-error').textContent).toBeTruthy();
        });
        
        it('should require departure time', () => {
            document.getElementById('start-lat').value = '51';
            document.getElementById('start-lon').value = '17';
            document.getElementById('end-lat').value = '51';
            document.getElementById('end-lon').value = '17';
            document.getElementById('departure-time').value = '';
            
            const result = validateInputs();
            expect(result).toBe(false);
            expect(document.getElementById('departure-time-error').textContent).toBeTruthy();
        });
        
        it('should validate limit range', () => {
            document.getElementById('start-lat').value = '51';
            document.getElementById('start-lon').value = '17';
            document.getElementById('end-lat').value = '51';
            document.getElementById('end-lon').value = '17';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            document.getElementById('result-limit').value = '25';
            
            const result = validateInputs();
            expect(result).toBe(false);
            expect(document.getElementById('result-limit-error').textContent).toBeTruthy();
        });
        
        it('should pass with valid inputs', () => {
            document.getElementById('start-lat').value = '51.1';
            document.getElementById('start-lon').value = '17.0';
            document.getElementById('end-lat').value = '51.2';
            document.getElementById('end-lon').value = '17.1';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            document.getElementById('result-limit').value = '5';
            
            const result = validateInputs();
            expect(result).toBe(true);
        });
    });
    
    describe('showValidationError', () => {
        it('should display error message', () => {
            showValidationError('start-lat', 'Invalid value');
            const errorEl = document.getElementById('start-lat-error');
            expect(errorEl.textContent).toBe('Invalid value');
        });
        
        it('should add error styling to input', () => {
            showValidationError('start-lat', 'Invalid value');
            const inputEl = document.getElementById('start-lat');
            expect(inputEl.classList.contains('border-red-500')).toBe(true);
        });
    });
    
    describe('handleFindDepartures', () => {
        it('should not call API with invalid inputs', async () => {
            document.getElementById('start-lat').value = 'invalid';
            
            await handleFindDepartures();
            expect(global.fetchClosestDepartures).not.toHaveBeenCalled();
        });
        
        it('should call API with valid inputs', async () => {
            document.getElementById('start-lat').value = '51.1';
            document.getElementById('start-lon').value = '17.0';
            document.getElementById('end-lat').value = '51.2';
            document.getElementById('end-lon').value = '17.1';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            document.getElementById('result-limit').value = '5';
            
            await handleFindDepartures();
            expect(global.fetchClosestDepartures).toHaveBeenCalledWith(
                { lat: 51.1, lon: 17.0 },
                { lat: 51.2, lon: 17.1 },
                jasmine.any(String),
                5
            );
        });
        
        it('should disable button during API call', async () => {
            document.getElementById('start-lat').value = '51.1';
            document.getElementById('start-lon').value = '17.0';
            document.getElementById('end-lat').value = '51.2';
            document.getElementById('end-lon').value = '17.1';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            
            let resolvePromise;
            global.fetchClosestDepartures = jasmine.createSpy('fetchClosestDepartures')
                .and.returnValue(new Promise(resolve => { resolvePromise = resolve; }));
            
            const promise = handleFindDepartures();
            const btn = document.getElementById('find-departures-btn');
            expect(btn.disabled).toBe(true);
            
            resolvePromise({});
            await promise;
            expect(btn.disabled).toBe(false);
        });
        
        it('should show loading spinner during API call', async () => {
            document.getElementById('start-lat').value = '51.1';
            document.getElementById('start-lon').value = '17.0';
            document.getElementById('end-lat').value = '51.2';
            document.getElementById('end-lon').value = '17.1';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            
            let resolvePromise;
            global.fetchClosestDepartures = jasmine.createSpy('fetchClosestDepartures')
                .and.returnValue(new Promise(resolve => { resolvePromise = resolve; }));
            
            const promise = handleFindDepartures();
            const spinner = document.getElementById('loading-spinner');
            expect(spinner.classList.contains('hidden')).toBe(false);
            
            resolvePromise({});
            await promise;
            expect(spinner.classList.contains('hidden')).toBe(true);
        });
        
        it('should re-enable button on error', async () => {
            document.getElementById('start-lat').value = '51.1';
            document.getElementById('start-lon').value = '17.0';
            document.getElementById('end-lat').value = '51.2';
            document.getElementById('end-lon').value = '17.1';
            document.getElementById('departure-time').value = '2024-01-01T10:00';
            
            global.fetchClosestDepartures = jasmine.createSpy('fetchClosestDepartures')
                .and.returnValue(Promise.reject(new Error('API error')));
            
            await handleFindDepartures();
            const btn = document.getElementById('find-departures-btn');
            expect(btn.disabled).toBe(false);
        });
    });
});

describe('Map Functionality (in api.js)', () => {
    beforeEach(() => {
        global.L = {
            marker: jasmine.createSpy('marker').and.returnValue({
                bindPopup: jasmine.createSpy('bindPopup').and.returnValue({})
            }),
            layerGroup: jasmine.createSpy('layerGroup').and.returnValue({
                addTo: jasmine.createSpy('addTo').and.returnValue({
                    clearLayers: jasmine.createSpy('clearLayers'),
                    addLayer: jasmine.createSpy('addLayer'),
                    getLayers: jasmine.createSpy('getLayers').and.returnValue([{}]),
                    getBounds: jasmine.createSpy('getBounds').and.returnValue({})
                })
            })
        };
        global.map = {
            fitBounds: jasmine.createSpy('fitBounds')
        };
    });
    
    afterEach(() => {
        delete global.L;
        delete global.map;
        delete global.markersLayer;
    });
    
    describe('marker initialization', () => {
        it('should create markers with correct coordinates', () => {
            const departures = [{
                stop_lat: 51.1079,
                stop_lon: 17.0385,
                stop_name: 'Test Stop'
            }];
            
            addStopMarkers(departures);
            expect(global.L.marker).toHaveBeenCalledWith([51.1079, 17.0385]);
        });
        
        it('should bind popup with departure info', () => {
            const departures = [{
                stop_lat: 51.1,
                stop_lon: 17.0,
                stop_name: 'Test Stop',
                route_id: '10',
                trip_headsign: 'Downtown'
            }];
            
            addStopMarkers(departures);
            const marker = global.L.marker.calls.mostRecent().returnValue;
            expect(marker.bindPopup).toHaveBeenCalledWith(jasmine.stringContaining('Test Stop'));
        });
    });
    
    describe('coordinate validation', () => {
        it('should handle valid Wroclaw coordinates', () => {
            const departures = [{
                stop_lat: 51.1079,
                stop_lon: 17.0385,
                stop_name: 'Wroclaw Main'
            }];
            
            addStopMarkers(departures);
            expect(global.L.marker).toHaveBeenCalled();
        });
        
        it('should skip invalid coordinates', () => {
            const departures = [
                { stop_lat: null, stop_lon: 17.0, stop_name: 'Invalid 1' },
                { stop_lat: 51.1, stop_lon: null, stop_name: 'Invalid 2' },
                { stop_name: 'Invalid 3' }
            ];
            
            addStopMarkers(departures);
            expect(global.L.marker).not.toHaveBeenCalled();
        });
    });
    
    describe('clearing selections', () => {
        it('should clear existing markers', () => {
            const mockLayer = {
                clearLayers: jasmine.createSpy('clearLayers'),
                addLayer: jasmine.createSpy('addLayer'),
                getLayers: jasmine.createSpy('getLayers').and.returnValue([{}]),
                getBounds: jasmine.createSpy('getBounds').and.returnValue({})
            };
            global.markersLayer = mockLayer;
            
            const departures = [{
                stop_lat: 51.1,
                stop_lon: 17.0,
                stop_name: 'Test'
            }];
            
            addStopMarkers(departures);
            expect(mockLayer.clearLayers).toHaveBeenCalled();
        });
        
        it('should create new layer if none exists', () => {
            const departures = [{
                stop_lat: 51.1,
                stop_lon: 17.0,
                stop_name: 'Test'
            }];
            
            addStopMarkers(departures);
            expect(global.L.layerGroup).toHaveBeenCalled();
        });
    });
    
    describe('map bounds adjustment', () => {
        it('should fit bounds to show all markers', () => {
            const departures = [
                { stop_lat: 51.1, stop_lon: 17.0, stop_name: 'Stop 1' },
                { stop_lat: 51.2, stop_lon: 17.1, stop_name: 'Stop 2' }
            ];
            
            addStopMarkers(departures);
            expect(global.map.fitBounds).toHaveBeenCalled();
        });
    });
});
