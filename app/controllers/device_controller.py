from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.device import Device, Sensor, SensorReading
from app.config.database import db
from app.config.mqtt_client import publish_command
from datetime import datetime
import json
import uuid

# Create blueprint
device_bp = Blueprint('device', __name__, url_prefix='/device')

# Web routes
@device_bp.route('/')
@login_required
def index():
    """Display list of user's devices"""
    if current_user.is_admin:
        devices = Device.query.all()
    else:
        devices = Device.query.filter_by(user_id=current_user.id).all()
    
    return render_template('device/index.html', devices=devices)

@device_bp.route('/<int:device_id>')
@login_required
def view(device_id):
    """Display device details"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        flash('You do not have permission to view this device.', 'danger')
        return redirect(url_for('device.index'))
    
    # Get sensors for this device
    sensors = Sensor.query.filter_by(device_id=device.id).all()
    
    return render_template('device/view.html', device=device, sensors=sensors)

@device_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new device"""
    if request.method == 'POST':
        device_id = request.form.get('device_id', str(uuid.uuid4()))
        name = request.form.get('name')
        device_type = request.form.get('device_type')
        description = request.form.get('description')
        location = request.form.get('location')
        ip_address = request.form.get('ip_address')
        mac_address = request.form.get('mac_address')
        firmware_version = request.form.get('firmware_version')
        
        # Create new device
        new_device = Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            user_id=current_user.id,
            description=description,
            location=location,
            ip_address=ip_address,
            mac_address=mac_address,
            firmware_version=firmware_version
        )
        
        db.session.add(new_device)
        db.session.commit()
        
        flash('Device added successfully.', 'success')
        return redirect(url_for('device.view', device_id=new_device.id))
    
    return render_template('device/add.html')

@device_bp.route('/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(device_id):
    """Edit device details"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        flash('You do not have permission to edit this device.', 'danger')
        return redirect(url_for('device.index'))
    
    if request.method == 'POST':
        device.name = request.form.get('name')
        device.device_type = request.form.get('device_type')
        device.description = request.form.get('description')
        device.location = request.form.get('location')
        device.ip_address = request.form.get('ip_address')
        device.mac_address = request.form.get('mac_address')
        device.firmware_version = request.form.get('firmware_version')
        
        db.session.commit()
        
        flash('Device updated successfully.', 'success')
        return redirect(url_for('device.view', device_id=device.id))
    
    return render_template('device/edit.html', device=device)

@device_bp.route('/<int:device_id>/delete', methods=['POST'])
@login_required
def delete(device_id):
    """Delete a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        flash('You do not have permission to delete this device.', 'danger')
        return redirect(url_for('device.index'))
    
    db.session.delete(device)
    db.session.commit()
    
    flash('Device deleted successfully.', 'success')
    return redirect(url_for('device.index'))

@device_bp.route('/<int:device_id>/control', methods=['GET', 'POST'])
@login_required
def control(device_id):
    """Control device interface"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        flash('You do not have permission to control this device.', 'danger')
        return redirect(url_for('device.index'))
    
    if request.method == 'POST':
        command = request.form.get('command')
        params = {}
        
        # Extract parameters from form data
        for key, value in request.form.items():
            if key.startswith('param_'):
                param_name = key[6:]  # Remove 'param_' prefix
                params[param_name] = value
        
        # Send command via MQTT
        success = publish_command(device.device_id, command, params)
        
        if success:
            flash(f'Command {command} sent successfully.', 'success')
        else:
            flash('Failed to send command.', 'danger')
        
        return redirect(url_for('device.control', device_id=device.id))
    
    return render_template('device/control.html', device=device)

# API Routes for devices
@device_bp.route('/api/devices', methods=['GET'])
@login_required
def api_get_devices():
    """API endpoint to get all devices for the user"""
    if current_user.is_admin:
        devices = Device.query.all()
    else:
        devices = Device.query.filter_by(user_id=current_user.id).all()
    
    return jsonify([device.to_dict() for device in devices])

@device_bp.route('/api/devices/<int:device_id>', methods=['GET'])
@login_required
def api_get_device(device_id):
    """API endpoint to get a specific device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(device.to_dict())

@device_bp.route('/api/devices', methods=['POST'])
@login_required
def api_add_device():
    """API endpoint to add a new device"""
    data = request.get_json()
    
    required_fields = ['name', 'device_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    device_id = data.get('device_id', str(uuid.uuid4()))
    
    # Create new device
    new_device = Device(
        device_id=device_id,
        name=data['name'],
        device_type=data['device_type'],
        user_id=current_user.id,
        description=data.get('description'),
        location=data.get('location'),
        ip_address=data.get('ip_address'),
        mac_address=data.get('mac_address'),
        firmware_version=data.get('firmware_version')
    )
    
    # Set configuration if provided
    if 'config' in data:
        new_device.set_config(data['config'])
    
    # Set metadata if provided
    if 'metadata' in data:
        new_device.set_metadata(data['metadata'])
    
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify(new_device.to_dict()), 201

@device_bp.route('/api/devices/<int:device_id>', methods=['PUT'])
@login_required
def api_update_device(device_id):
    """API endpoint to update a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update device fields
    if 'name' in data:
        device.name = data['name']
    if 'device_type' in data:
        device.device_type = data['device_type']
    if 'description' in data:
        device.description = data['description']
    if 'location' in data:
        device.location = data['location']
    if 'ip_address' in data:
        device.ip_address = data['ip_address']
    if 'mac_address' in data:
        device.mac_address = data['mac_address']
    if 'firmware_version' in data:
        device.firmware_version = data['firmware_version']
    
    # Update configuration if provided
    if 'config' in data:
        device.set_config(data['config'])
    
    # Update metadata if provided
    if 'metadata' in data:
        device.set_metadata(data['metadata'])
    
    db.session.commit()
    
    return jsonify(device.to_dict())

@device_bp.route('/api/devices/<int:device_id>', methods=['DELETE'])
@login_required
def api_delete_device(device_id):
    """API endpoint to delete a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({'message': 'Device deleted successfully'}), 200

@device_bp.route('/api/devices/<int:device_id>/control', methods=['POST'])
@login_required
def api_device_control(device_id):
    """API endpoint to send control commands to a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'command' not in data:
        return jsonify({'error': 'Missing required field: command'}), 400
    
    command = data['command']
    params = data.get('params', {})
    
    # Send command via MQTT
    success = publish_command(device.device_id, command, params)
    
    if success:
        return jsonify({'message': f'Command {command} sent successfully'}), 200
    else:
        return jsonify({'error': 'Failed to send command'}), 500

# API routes for sensors
@device_bp.route('/api/devices/<int:device_id>/sensors', methods=['GET'])
@login_required
def api_get_sensors(device_id):
    """API endpoint to get all sensors for a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sensors = Sensor.query.filter_by(device_id=device.id).all()
    
    return jsonify([sensor.to_dict() for sensor in sensors])

@device_bp.route('/api/devices/<int:device_id>/sensors', methods=['POST'])
@login_required
def api_add_sensor(device_id):
    """API endpoint to add a new sensor to a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    required_fields = ['sensor_id', 'name', 'sensor_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new sensor
    new_sensor = Sensor(
        sensor_id=data['sensor_id'],
        name=data['name'],
        sensor_type=data['sensor_type'],
        device_id=device.id,
        unit=data.get('unit'),
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        description=data.get('description')
    )
    
    db.session.add(new_sensor)
    db.session.commit()
    
    return jsonify(new_sensor.to_dict()), 201

@device_bp.route('/api/sensors/<int:sensor_id>/readings', methods=['GET'])
@login_required
def api_get_sensor_readings(sensor_id):
    """API endpoint to get readings for a sensor"""
    sensor = Sensor.query.get_or_404(sensor_id)
    device = Device.query.get(sensor.device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get optional query parameters
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    # Build query
    query = SensorReading.query.filter_by(sensor_id=sensor.id)
    
    if start_time:
        query = query.filter(SensorReading.timestamp >= start_time)
    
    if end_time:
        query = query.filter(SensorReading.timestamp <= end_time)
    
    # Order by timestamp descending and limit results
    readings = query.order_by(SensorReading.timestamp.desc()).limit(limit).all()
    
    return jsonify([reading.to_dict() for reading in readings])

@device_bp.route('/api/sensors/<int:sensor_id>/readings', methods=['POST'])
@login_required
def api_add_sensor_reading(sensor_id):
    """API endpoint to add a new reading for a sensor"""
    sensor = Sensor.query.get_or_404(sensor_id)
    device = Device.query.get(sensor.device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'value' not in data:
        return jsonify({'error': 'Missing required field: value'}), 400
    
    timestamp = data.get('timestamp', datetime.utcnow())
    
    # Create new reading
    new_reading = SensorReading(
        value=data['value'],
        sensor_id=sensor.id,
        timestamp=timestamp
    )
    
    db.session.add(new_reading)
    db.session.commit()
    
    return jsonify(new_reading.to_dict()), 201 