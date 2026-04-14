/**
 * Pollution & Traffic Optimizer - Frontend Application
 */
// Configuration
const API_BASE = '';
const DEFAULT_CITY = 'pune';
const REFRESH_INTERVAL = 60000; // 1 minute

// State
let map = null;
let markers = [];
let heatmapLayer = null;
let currentCity = DEFAULT_CITY;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initializing...');
    initMap();
    loadDashboard();
    setupEventListeners();
    startAutoRefresh();
});

/**
 * Initialize Leaflet map
 */
function initMap() {
    // Pune coordinates
    const defaultCenter = [18.5204, 73.8567];
    
    map = L.map('map').setView(defaultCenter, 12);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    console.log('Map initialized');
}

/**
 * Load all dashboard data
 */
async function loadDashboard() {
    showLoading(true);
    
    try {
        await Promise.all([
            loadCurrentAQI(),
            loadPredictions(),
            loadAlerts(),
            loadTrafficHeatmap(),
            loadBestTravelTime()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
    
    showLoading(false);
}

/**
 * Load current AQI data
 */
async function loadCurrentAQI() {
    try {
        const response = await fetch(`${API_BASE}/api/aqi/${currentCity}`);
        if (!response.ok) throw new Error('AQI fetch failed');
        const data = await response.json();
        
        updateAQIDisplay(data);
        updateAQIMap(data);
    } catch (error) {
        console.error('Error loading AQI:', error);
        document.getElementById('aqi-value').textContent = 'Error';
    }
}

/**
 * Update AQI display elements
 */
function updateAQIDisplay(data) {
    const aqiValue = document.getElementById('aqi-value');
    const aqiCategory = document.getElementById('aqi-category');
    const aqiCard = document.getElementById('aqi-card');
    
    if (aqiValue) {
        aqiValue.textContent = data.aqi;
        aqiValue.className = `aqi-number ${getAQIClass(data.aqi)}`;
    }
    
    if (aqiCategory) {
        aqiCategory.textContent = data.category;
    }
    
    if (aqiCard) {
        aqiCard.className = `card aqi-card ${getAQIClass(data.aqi)}`;
    }
    
    updatePollutantDetails(data);
    updateWeatherInfo(data);
}

/**
 * Update pollutant details
 */
function updatePollutantDetails(data) {
    const details = document.getElementById('pollutant-details');
    if (!details) return;
    
    details.innerHTML = `
        <div class="pollutant-item">
            <span class="pollutant-label">PM2.5</span>
            <span class="pollutant-value">${data.pm25?.toFixed(1) || 'N/A'} µg/m³</span>
        </div>
        <div class="pollutant-item">
            <span class="pollutant-label">PM10</span>
            <span class="pollutant-value">${data.pm10?.toFixed(1) || 'N/A'} µg/m³</span>
        </div>
        <div class="pollutant-item">
            <span class="pollutant-label">O₃</span>
            <span class="pollutant-value">${data.o3?.toFixed(1) || 'N/A'} ppb</span>
        </div>
        <div class="pollutant-item">
            <span class="pollutant-label">NO₂</span>
            <span class="pollutant-value">${data.no2?.toFixed(1) || 'N/A'} ppb</span>
        </div>
    `;
}

/**
 * Update weather information
 */
function updateWeatherInfo(data) {
    const weather = document.getElementById('weather-info');
    if (!weather) return;
    
    weather.innerHTML = `
        <div class="weather-item">
            <i class="fas fa-thermometer-half"></i>
            <span>${data.temperature?.toFixed(1) || 'N/A'}°C</span>
        </div>
        <div class="weather-item">
            <i class="fas fa-tint"></i>
            <span>${data.humidity?.toFixed(0) || 'N/A'}%</span>
        </div>
        <div class="weather-item">
            <i class="fas fa-wind"></i>
            <span>${data.wind_speed?.toFixed(1) || 'N/A'} m/s</span>
        </div>
    `;
}

/**
 * Load predictions
 */
async function loadPredictions() {
    try {
        const response = await fetch(`${API_BASE}/api/predictions/${currentCity}`);
        if (!response.ok) throw new Error('Predictions fetch failed');
        const data = await response.json();
        
        updatePredictionDisplay(data);
    } catch (error) {
        console.error('Error loading predictions:', error);
        document.getElementById('predictions').innerHTML = '<p>Failed to load predictions</p>';
    }
}

/**
 * Update prediction display
 */
function updatePredictionDisplay(data) {
    const container = document.getElementById('predictions');
    if (!container) return;
    
    const trendIcon = getTrendIcon(data.trend);
    const trendClass = data.trend === 'improving' ? 'trend-good' : 
                       data.trend === 'worsening' ? 'trend-bad' : 'trend-stable';
    
    container.innerHTML = `
        <div class="prediction-row">
            <div class="prediction-item">
                <span class="prediction-label">Current</span>
                <span class="prediction-value ${getAQIClass(data.current_aqi)}">${data.current_aqi}</span>
                <span class="prediction-category">${data.current_category}</span>
            </div>
            <div class="prediction-arrow">
                <i class="fas ${trendIcon} ${trendClass}"></i>
            </div>
            <div class="prediction-item">
                <span class="prediction-label">In 2 Hours</span>
                <span class="prediction-value ${getAQIClass(data.predicted_2hr)}">${data.predicted_2hr}</span>
                <span class="prediction-category">${data.category_2hr}</span>
            </div>
            <div class="prediction-arrow">
                <i class="fas ${trendIcon} ${trendClass}"></i>
            </div>
            <div class="prediction-item">
                <span class="prediction-label">In 4 Hours</span>
                <span class="prediction-value ${getAQIClass(data.predicted_4hr)}">${data.predicted_4hr}</span>
                <span class="prediction-category">${data.category_4hr}</span>
            </div>
        </div>
        <div class="prediction-confidence">
            <span>Confidence: ${(data.confidence * 100).toFixed(0)}%</span>
        </div>
    `;
}

/**
 * Load alerts
 */
async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/api/predictions/${currentCity}/alerts`);
        if (!response.ok) throw new Error('Alerts fetch failed');
        const alerts = await response.json();
        
        updateAlertsDisplay(alerts);
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

/**
 * Update alerts display
 */
function updateAlertsDisplay(alerts) {
    const container = document.getElementById('alerts');
    if (!container) return;
    
    if (alerts.length === 0) {
        container.innerHTML = '<p class="no-alerts">No active alerts</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert alert-${alert.alert_type}">
            <div class="alert-header">
                <i class="fas ${getAlertIcon(alert.alert_type)}"></i>
                <span class="alert-title">${alert.title}</span>
            </div>
            <p class="alert-message">${alert.message}</p>
            <ul class="alert-actions">
                ${alert.actions.map(action => `<li>${action}</li>`).join('')}
            </ul>
        </div>
    `).join('');
}

/**
 * Load traffic heatmap
 */
async function loadTrafficHeatmap() {
    try {
        const response = await fetch(`${API_BASE}/api/traffic/${currentCity}/heatmap`);
        if (!response.ok) throw new Error('Heatmap fetch failed');
        const data = await response.json();
        
        updateHeatmap(data);
    } catch (error) {
        console.error('Error loading heatmap:', error);
    }
}

/**
 * Update heatmap layer
 */
function updateHeatmap(data) {
    if (heatmapLayer && map) {
        map.removeLayer(heatmapLayer);
    }
    
    if (!map) return;
    
    const heatData = data.points.map(p => [p.lat, p.lng, p.intensity]);
    
    if (typeof L.heatLayer === 'function') {
        heatmapLayer = L.heatLayer(heatData, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            gradient: {
                0.4: 'blue',
                0.6: 'lime',
                0.8: 'yellow',
                1.0: 'red'
            }
        }).addTo(map);
    }
}

/**
 * Load best travel time recommendations
 */
async function loadBestTravelTime() {
    try {
        const response = await fetch(`${API_BASE}/api/predictions/${currentCity}/best-time`);
        if (!response.ok) throw new Error('Best time fetch failed');
        const data = await response.json();
        
        updateBestTimeDisplay(data);
    } catch (error) {
        console.error('Error loading best time:', error);
    }
}

/**
 * Update best time display
 */
function updateBestTimeDisplay(data) {
    const container = document.getElementById('best-time');
    if (!container) return;
    
    container.innerHTML = `
        <div class="recommendations">
            ${data.recommendations.map(rec => `
                <div class="recommendation-item">
                    <span class="time-slot">${rec.time_slot}</span>
                    <span class="expected-aqi ${getAQIClass(rec.expected_aqi)}">AQI: ${rec.expected_aqi}</span>
                    <p class="recommendation-text">${rec.recommendation}</p>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Update AQI markers on map
 */
function updateAQIMap(data) {
    if (!map) return;
    
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    
    const coords = getCityCoordinates(currentCity);
    if (coords) {
        const marker = L.circleMarker(coords, {
            radius: 20,
            fillColor: getAQIColor(data.aqi),
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup(`
            <div class="popup-content">
                <h4>${currentCity.charAt(0).toUpperCase() + currentCity.slice(1)}</h4>
                <p class="popup-aqi ${getAQIClass(data.aqi)}">AQI: ${data.aqi}</p>
                <p class="popup-category">${data.category}</p>
            </div>
        `);
        
        markers.push(marker);
    }
}

/**
 * Handle route optimization
 */
async function optimizeRoute() {
    const originInput = document.getElementById('origin');
    const destInput = document.getElementById('destination');
    const preference = document.getElementById('route-preference')?.value || 'balanced';
    
    if (!originInput?.value || !destInput?.value) {
        showError('Please enter origin and destination');
        return;
    }
    
    showLoading(true);
    
    try {
        const origin = getCityCoordinates(currentCity);
        const dest = [origin[0] + 0.05, origin[1] + 0.05];
        
        const response = await fetch(`${API_BASE}/api/routes/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                origin: { latitude: origin[0], longitude: origin[1] },
                destination: { latitude: dest[0], longitude: dest[1] },
                preference: preference
            })
        });
        
        if (!response.ok) throw new Error('Route optimization failed');
        const data = await response.json();
        displayRouteResult(data);
    } catch (error) {
        console.error('Error optimizing route:', error);
        showError('Failed to optimize route');
    }
    
    showLoading(false);
}

/**
 * Display route optimization result
 */
function displayRouteResult(data) {
    const container = document.getElementById('route-result');
    if (!container) return;
    
    const route = data.recommended_route;
    
    container.innerHTML = `
        <div class="route-card">
            <h4>${route.name}</h4>
            <div class="route-stats">
                <div class="stat">
                    <i class="fas fa-road"></i>
                    <span>${route.total_distance_km} km</span>
                </div>
                <div class="stat">
                    <i class="fas fa-clock"></i>
                    <span>${route.estimated_time_minutes} min</span>
                </div>
                <div class="stat">
                    <i class="fas fa-lungs"></i>
                    <span>Avg AQI: ${route.average_aqi.toFixed(0)}</span>
                </div>
            </div>
            <p class="route-reason">${route.recommendation_reason}</p>
            
            ${data.savings ? `
                <div class="savings">
                    <h5>Compared to fastest route:</h5>
                    <p>Pollution reduction: ${data.savings.pollution_reduction_percent}%</p>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const citySelect = document.getElementById('city-select');
    if (citySelect) {
        citySelect.addEventListener('change', (e) => {
            currentCity = e.target.value;
            loadDashboard();
        });
    }
    
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboard);
    }
    
    const optimizeBtn = document.getElementById('optimize-btn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizeRoute);
    }
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    setInterval(() => {
        loadCurrentAQI();
        loadPredictions();
    }, REFRESH_INTERVAL);
}

// Utility functions
function getAQIClass(aqi) {
    if (aqi <= 50) return 'aqi-good';
    if (aqi <= 100) return 'aqi-moderate';
    if (aqi <= 150) return 'aqi-sensitive';
    if (aqi <= 200) return 'aqi-unhealthy';
    if (aqi <= 300) return 'aqi-very-unhealthy';
    return 'aqi-hazardous';
}

function getAQIColor(aqi) {
    if (aqi <= 50) return '#00E400';
    if (aqi <= 100) return '#FFFF00';
    if (aqi <= 150) return '#FF7E00';
    if (aqi <= 200) return '#FF0000';
    if (aqi <= 300) return '#8F3F97';
    return '#7E0023';
}

function getTrendIcon(trend) {
    switch (trend) {
        case 'improving': return 'fa-arrow-down';
        case 'worsening': return 'fa-arrow-up';
        default: return 'fa-minus';
    }
}

function getAlertIcon(type) {
    switch (type) {
        case 'critical': return 'fa-exclamation-circle';
        case 'danger': return 'fa-exclamation-triangle';
        case 'warning': return 'fa-exclamation';
        default: return 'fa-info-circle';
    }
}

function getCityCoordinates(city) {
    const coords = {
        'pune': [18.5204, 73.8567],
        'mumbai': [19.0760, 72.8777],
        'delhi': [28.6139, 77.2090],
        'bangalore': [12.9716, 77.5946],
        'chennai': [13.0827, 80.2707],
        'hyderabad': [17.3850, 78.4867],
        'kolkata': [22.5726, 88.3639]
    };
    return coords[city.toLowerCase()] || coords['pune'];
}

function showLoading(show) {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}

function showError(message) {
    const toast = document.getElementById('error-toast');
    if (toast) {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
}