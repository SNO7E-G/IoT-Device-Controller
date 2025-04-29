# API Documentation

This document provides detailed information about the RESTful API endpoints available in the IoT Device Controller application.

## Authentication

All API endpoints require authentication. Authentication is handled via session cookies for web interface and API requests.

- To access the API, the user must be logged in.
- Unauthorized access will result in a 401 or 403 error response.

## General Response Format

API responses are provided in JSON format and typically follow this structure:

```json
{
    "data": { /* Response data */ },
    "message": "Success message (optional)",
    "error": "Error message (in case of errors)"
}
```

## Error Handling

Error responses will include an appropriate HTTP status code and an error message in the response body:

```json
{
    "error": "Detailed error message"
}
```

Common error codes:
- 400: Bad Request - The request was malformed
- 401: Unauthorized - Authentication is required
- 403: Forbidden - The user doesn't have access to the requested resource
- 404: Not Found - The requested resource doesn't exist
- 500: Internal Server Error - An unexpected error occurred on the server

## Device Endpoints

### List Devices

Retrieves a list of devices accessible by the authenticated user.

- **URL**: `/device/api/devices`
- **Method**: `GET`
- **URL Parameters**: None
- **Query Parameters**:
  - `type` (optional): Filter devices by type
  - `status` (optional): Filter devices by status (online/offline)
  - `location` (optional): Filter devices by location
- **Success Response**:
  - **Code**: 200
  - **Content**: List of device objects
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/device/api/devices -H "Content-Type: application/json"
  ```

### Get Device Details

Retrieves details for a specific device.

- **URL**: `/device/api/devices/<device_id>`
- **Method**: `GET`
- **URL Parameters**:
  - `device_id`: ID of the device to retrieve
- **Success Response**:
  - **Code**: 200
  - **Content**: Device object with detailed information
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/device/api/devices/1 -H "Content-Type: application/json"
  ```

### Create Device

Adds a new IoT device to the system.

- **URL**: `/device/api/devices`
- **Method**: `POST`
- **Data Parameters**:
  ```json
  {
    "name": "Living Room Light",
    "device_type": "light",
    "description": "Smart light in the living room",
    "location": "Living Room",
    "ip_address": "192.168.1.100",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "firmware_version": "1.2.3",
    "config": {
      "brightness": 75,
      "color": "#FFFFFF"
    }
  }
  ```
- **Required Fields**: `name`, `device_type`
- **Success Response**:
  - **Code**: 201
  - **Content**: The created device object
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Missing required field: name"}`
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/device/api/devices -H "Content-Type: application/json" -d '{"name": "Living Room Light", "device_type": "light", "location": "Living Room"}'
  ```

### Update Device

Updates an existing device's information.

- **URL**: `/device/api/devices/<device_id>`
- **Method**: `PUT`
- **URL Parameters**:
  - `device_id`: ID of the device to update
- **Data Parameters**: Same as for device creation, all fields optional
- **Success Response**:
  - **Code**: 200
  - **Content**: The updated device object
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
- **Example**:
  ```bash
  curl -X PUT http://localhost:5000/device/api/devices/1 -H "Content-Type: application/json" -d '{"name": "Updated Light Name", "location": "Kitchen"}'
  ```

### Delete Device

Removes a device from the system.

- **URL**: `/device/api/devices/<device_id>`
- **Method**: `DELETE`
- **URL Parameters**:
  - `device_id`: ID of the device to delete
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"message": "Device deleted successfully"}`
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
- **Example**:
  ```bash
  curl -X DELETE http://localhost:5000/device/api/devices/1 -H "Content-Type: application/json"
  ```

### Control Device

Sends a command to control a device.

- **URL**: `/device/api/devices/<device_id>/control`
- **Method**: `POST`
- **URL Parameters**:
  - `device_id`: ID of the device to control
- **Data Parameters**:
  ```json
  {
    "command": "turn_on",
    "params": {
      "brightness": 80,
      "color": "#FFD700"
    }
  }
  ```
- **Required Fields**: `command`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"message": "Command turn_on sent successfully"}`
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
  - **Code**: 500
  - **Content**: `{"error": "Failed to send command"}`
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/device/api/devices/1/control -H "Content-Type: application/json" -d '{"command": "turn_on", "params": {"brightness": 80}}'
  ```

## Sensor Endpoints

### Get Device Sensors

Retrieves all sensors for a specific device.

- **URL**: `/device/api/devices/<device_id>/sensors`
- **Method**: `GET`
- **URL Parameters**:
  - `device_id`: ID of the device
- **Success Response**:
  - **Code**: 200
  - **Content**: List of sensor objects
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
- **Example**:
  ```bash
  curl -X GET http://localhost:5000/device/api/devices/1/sensors -H "Content-Type: application/json"
  ```

### Add Sensor to Device

Adds a new sensor to a device.

- **URL**: `/device/api/devices/<device_id>/sensors`
- **Method**: `POST`
- **URL Parameters**:
  - `device_id`: ID of the device
- **Data Parameters**:
  ```json
  {
    "sensor_id": "temp_sensor_01",
    "name": "Temperature Sensor",
    "sensor_type": "temperature",
    "unit": "°C",
    "min_value": -20,
    "max_value": 100,
    "description": "Indoor temperature sensor"
  }
  ```
- **Required Fields**: `sensor_id`, `name`, `sensor_type`
- **Success Response**:
  - **Code**: 201
  - **Content**: The created sensor object
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Device not found"}`
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/device/api/devices/1/sensors -H "Content-Type: application/json" -d '{"sensor_id": "temp_sensor_01", "name": "Temperature Sensor", "sensor_type": "temperature"}'
  ```

### Get Sensor Readings

Retrieves readings for a specific sensor.

- **URL**: `/device/api/sensors/<sensor_id>/readings`
- **Method**: `GET`
- **URL Parameters**:
  - `sensor_id`: ID of the sensor
- **Query Parameters**:
  - `start_time` (optional): Start time for filtering readings (ISO format)
  - `end_time` (optional): End time for filtering readings (ISO format)
  - `limit` (optional): Maximum number of readings to return (default: 100)
- **Success Response**:
  - **Code**: 200
  - **Content**: List of sensor reading objects
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Sensor not found"}`
- **Example**:
  ```bash
  curl -X GET "http://localhost:5000/device/api/sensors/1/readings?limit=50&start_time=2023-01-01T00:00:00Z" -H "Content-Type: application/json"
  ```

### Add Sensor Reading

Adds a new reading for a sensor.

- **URL**: `/device/api/sensors/<sensor_id>/readings`
- **Method**: `POST`
- **URL Parameters**:
  - `sensor_id`: ID of the sensor
- **Data Parameters**:
  ```json
  {
    "value": 24.5,
    "timestamp": "2023-06-15T13:45:30Z"
  }
  ```
- **Required Fields**: `value`
- **Success Response**:
  - **Code**: 201
  - **Content**: The created sensor reading object
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"error": "Sensor not found"}`
- **Example**:
  ```bash
  curl -X POST http://localhost:5000/device/api/sensors/1/readings -H "Content-Type: application/json" -d '{"value": 24.5}'
  ```

## Data Models

### Device Object

```json
{
  "id": 1,
  "device_id": "device_123456",
  "name": "Living Room Light",
  "device_type": "light",
  "description": "Smart light in the living room",
  "status": "online",
  "location": "Living Room",
  "ip_address": "192.168.1.100",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "firmware_version": "1.2.3",
  "last_seen": "2023-06-15T13:45:30Z",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-06-15T13:45:30Z",
  "config": {
    "brightness": 75,
    "color": "#FFFFFF"
  },
  "metadata": {
    "manufacturer": "Example Corp",
    "model": "Smart Light 2000"
  },
  "user_id": 1
}
```

### Sensor Object

```json
{
  "id": 1,
  "sensor_id": "temp_sensor_01",
  "name": "Temperature Sensor",
  "sensor_type": "temperature",
  "unit": "°C",
  "min_value": -20,
  "max_value": 100,
  "description": "Indoor temperature sensor",
  "device_id": 1,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Sensor Reading Object

```json
{
  "id": 1,
  "value": 24.5,
  "timestamp": "2023-06-15T13:45:30Z",
  "sensor_id": 1
}
```

---

© 2024 Mahmoud Ashraf (SNO7E). All rights reserved. 