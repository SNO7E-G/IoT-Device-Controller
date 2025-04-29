// Main JavaScript for IoT Device Controller

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize WebSocket connection if user is logged in
    initWebSocket();
    
    // Initialize dashboard charts if on dashboard page
    if (document.getElementById('deviceTypeChart')) {
        initDashboardCharts();
    }
    
    // Initialize device control handlers if on device control page
    if (document.querySelector('.device-control-form')) {
        initDeviceControls();
    }
    
    // Initialize sensor charts if on device view page with sensor data
    if (document.querySelector('.sensor-chart')) {
        initSensorCharts();
    }
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Initialize WebSocket connection for real-time updates
 */
function initWebSocket() {
    // Check if SocketIO is available (should be loaded in templates where needed)
    if (typeof io !== 'undefined') {
        // Connect to WebSocket
        const socket = io();
        
        // Connection established
        socket.on('connect', function() {
            console.log('WebSocket connected');
        });
        
        // Handle device status updates
        socket.on('device_status', function(data) {
            updateDeviceStatus(data.device_id, data.data);
        });
        
        // Handle device telemetry data
        socket.on('device_telemetry', function(data) {
            updateDeviceTelemetry(data.device_id, data.data);
        });
        
        // Handle command responses
        socket.on('device_response', function(data) {
            handleDeviceResponse(data.device_id, data.data);
        });
        
        // Connection lost
        socket.on('disconnect', function() {
            console.log('WebSocket disconnected');
        });
    }
}

/**
 * Update device status indicators in UI
 * @param {string} deviceId - The device ID
 * @param {object} statusData - Status data object
 */
function updateDeviceStatus(deviceId, statusData) {
    // Find all elements representing this device
    const deviceElements = document.querySelectorAll(`[data-device-id="${deviceId}"]`);
    
    deviceElements.forEach(element => {
        // Update status indicator
        const statusIndicator = element.querySelector('.device-status');
        if (statusIndicator) {
            statusIndicator.classList.remove('online', 'offline', 'error');
            statusIndicator.classList.add(statusData.status);
            statusIndicator.setAttribute('title', `Status: ${statusData.status}`);
        }
        
        // Update status text if exists
        const statusText = element.querySelector('.device-status-text');
        if (statusText) {
            statusText.textContent = statusData.status;
            
            // Also update classes for styling
            statusText.classList.remove('text-success', 'text-secondary', 'text-danger');
            if (statusData.status === 'online') {
                statusText.classList.add('text-success');
            } else if (statusData.status === 'offline') {
                statusText.classList.add('text-secondary');
            } else if (statusData.status === 'error') {
                statusText.classList.add('text-danger');
            }
        }
        
        // Update last seen timestamp if exists
        const lastSeen = element.querySelector('.device-last-seen');
        if (lastSeen && statusData.timestamp) {
            const date = new Date(statusData.timestamp);
            lastSeen.textContent = date.toLocaleString();
        }
    });
}

/**
 * Update device telemetry data in UI
 * @param {string} deviceId - The device ID
 * @param {object} telemetryData - Telemetry data object
 */
function updateDeviceTelemetry(deviceId, telemetryData) {
    // Find the device element
    const deviceElement = document.querySelector(`[data-device-id="${deviceId}"]`);
    if (!deviceElement) return;
    
    // Update sensor readings if they exist
    for (const [sensorId, value] of Object.entries(telemetryData.readings || {})) {
        const sensorElement = deviceElement.querySelector(`[data-sensor-id="${sensorId}"]`);
        if (sensorElement) {
            const valueElement = sensorElement.querySelector('.sensor-value');
            if (valueElement) {
                valueElement.textContent = value;
            }
            
            // Update chart if it exists
            updateSensorChart(sensorId, telemetryData.timestamp, value);
        }
    }
}

/**
 * Handle device command responses
 * @param {string} deviceId - The device ID
 * @param {object} responseData - Response data object
 */
function handleDeviceResponse(deviceId, responseData) {
    // Find the device control form
    const deviceForm = document.querySelector(`.device-control-form[data-device-id="${deviceId}"]`);
    if (!deviceForm) return;
    
    // Create response message
    const responseElement = document.createElement('div');
    responseElement.classList.add('alert', responseData.success ? 'alert-success' : 'alert-danger', 'mt-3');
    responseElement.textContent = responseData.message || (responseData.success ? 'Command executed successfully' : 'Command failed');
    
    // Add dismiss button
    const dismissButton = document.createElement('button');
    dismissButton.type = 'button';
    dismissButton.classList.add('btn-close');
    dismissButton.dataset.bsDismiss = 'alert';
    dismissButton.setAttribute('aria-label', 'Close');
    responseElement.appendChild(dismissButton);
    
    // Insert response message after form
    deviceForm.parentNode.insertBefore(responseElement, deviceForm.nextSibling);
    
    // Auto-remove after a few seconds
    setTimeout(() => {
        responseElement.remove();
    }, 5000);
}

/**
 * Initialize dashboard charts
 */
function initDashboardCharts() {
    // Fetch dashboard statistics
    fetch('/dashboard/api/stats')
        .then(response => response.json())
        .then(data => {
            // Create device type distribution chart
            const deviceTypeCtx = document.getElementById('deviceTypeChart').getContext('2d');
            new Chart(deviceTypeCtx, {
                type: 'doughnut',
                data: {
                    labels: data.device_types.labels,
                    datasets: [{
                        data: data.device_types.data,
                        backgroundColor: [
                            '#0d6efd', '#20c997', '#fd7e14', '#6610f2', '#d63384', '#ffc107'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Update device count stats
            document.getElementById('totalDevices').textContent = data.device_count.total;
            document.getElementById('onlineDevices').textContent = data.device_count.online;
            document.getElementById('offlineDevices').textContent = data.device_count.offline;
            document.getElementById('sensorCount').textContent = data.sensor_count;
            document.getElementById('readingCount').textContent = data.reading_count;
        })
        .catch(error => console.error('Error fetching dashboard stats:', error));
}

/**
 * Initialize device control handlers
 */
function initDeviceControls() {
    const deviceForms = document.querySelectorAll('.device-control-form');
    
    deviceForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const deviceId = this.dataset.deviceId;
            const command = this.querySelector('[name="command"]').value;
            
            // Collect parameters
            const params = {};
            this.querySelectorAll('[name^="param_"]').forEach(input => {
                const paramName = input.name.replace('param_', '');
                params[paramName] = input.value;
            });
            
            // Send command via API
            fetch(`/device/api/devices/${deviceId}/control`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command,
                    params: params
                })
            })
            .then(response => response.json())
            .then(data => {
                // Show response message
                const alertClass = data.error ? 'alert-danger' : 'alert-success';
                const message = data.error || data.message;
                
                const alertElement = document.createElement('div');
                alertElement.classList.add('alert', alertClass, 'mt-3');
                alertElement.textContent = message;
                
                // Add dismiss button
                const dismissButton = document.createElement('button');
                dismissButton.type = 'button';
                dismissButton.classList.add('btn-close');
                dismissButton.dataset.bsDismiss = 'alert';
                dismissButton.setAttribute('aria-label', 'Close');
                alertElement.appendChild(dismissButton);
                
                // Insert alert after form
                this.parentNode.insertBefore(alertElement, this.nextSibling);
                
                // Auto-remove after a few seconds
                setTimeout(() => {
                    alertElement.remove();
                }, 5000);
            })
            .catch(error => {
                console.error('Error sending command:', error);
                
                // Show error message
                const alertElement = document.createElement('div');
                alertElement.classList.add('alert', 'alert-danger', 'mt-3');
                alertElement.textContent = 'An error occurred while sending the command.';
                
                // Add dismiss button
                const dismissButton = document.createElement('button');
                dismissButton.type = 'button';
                dismissButton.classList.add('btn-close');
                dismissButton.dataset.bsDismiss = 'alert';
                dismissButton.setAttribute('aria-label', 'Close');
                alertElement.appendChild(dismissButton);
                
                // Insert alert after form
                this.parentNode.insertBefore(alertElement, this.nextSibling);
                
                // Auto-remove after a few seconds
                setTimeout(() => {
                    alertElement.remove();
                }, 5000);
            });
        });
    });
}

/**
 * Initialize sensor charts
 */
function initSensorCharts() {
    const deviceId = document.querySelector('[data-device-id]').dataset.deviceId;
    
    // Fetch sensor data
    fetch(`/dashboard/api/sensor-data/${deviceId}`)
        .then(response => response.json())
        .then(sensorData => {
            sensorData.forEach(sensor => {
                const chartCanvas = document.querySelector(`[data-sensor-id="${sensor.id}"] .sensor-chart`);
                if (!chartCanvas) return;
                
                // Create chart for this sensor
                const ctx = chartCanvas.getContext('2d');
                window.sensorCharts = window.sensorCharts || {};
                window.sensorCharts[sensor.id] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: sensor.data.labels,
                        datasets: [{
                            label: `${sensor.name} (${sensor.unit || ''})`,
                            data: sensor.data.values,
                            borderColor: '#0d6efd',
                            tension: 0.1,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Time'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: sensor.unit || 'Value'
                                }
                            }
                        }
                    }
                });
            });
        })
        .catch(error => console.error('Error fetching sensor data:', error));
}

/**
 * Update sensor chart with new data point
 * @param {string} sensorId - The sensor ID
 * @param {string} timestamp - The timestamp
 * @param {number} value - The sensor reading value
 */
function updateSensorChart(sensorId, timestamp, value) {
    if (!window.sensorCharts || !window.sensorCharts[sensorId]) return;
    
    const chart = window.sensorCharts[sensorId];
    
    // Format timestamp
    const date = new Date(timestamp);
    const timeLabel = date.toLocaleTimeString();
    
    // Add new data point
    chart.data.labels.push(timeLabel);
    chart.data.datasets[0].data.push(value);
    
    // Remove oldest data point if we have too many
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    
    // Update chart
    chart.update();
} 