from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.device import Device, Sensor, SensorReading
from app.config.database import db
from datetime import datetime, timedelta
from sqlalchemy import func

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view"""
    # Get device counts
    if current_user.is_admin:
        total_devices = Device.query.count()
        online_devices = Device.query.filter_by(status='online').count()
        offline_devices = Device.query.filter_by(status='offline').count()
        recent_devices = Device.query.order_by(Device.created_at.desc()).limit(5).all()
    else:
        total_devices = Device.query.filter_by(user_id=current_user.id).count()
        online_devices = Device.query.filter_by(user_id=current_user.id, status='online').count()
        offline_devices = Device.query.filter_by(user_id=current_user.id, status='offline').count()
        recent_devices = Device.query.filter_by(user_id=current_user.id).order_by(Device.created_at.desc()).limit(5).all()
    
    return render_template('dashboard/index.html', 
                           total_devices=total_devices,
                           online_devices=online_devices,
                           offline_devices=offline_devices,
                           recent_devices=recent_devices)

@dashboard_bp.route('/devices')
@login_required
def devices():
    """Dashboard devices view"""
    if current_user.is_admin:
        devices = Device.query.all()
    else:
        devices = Device.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard/devices.html', devices=devices)

@dashboard_bp.route('/analytics')
@login_required
def analytics():
    """Dashboard analytics view"""
    return render_template('dashboard/analytics.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    """Dashboard settings view"""
    return render_template('dashboard/settings.html')

@dashboard_bp.route('/alerts')
@login_required
def alerts():
    """Dashboard alerts view"""
    return render_template('dashboard/alerts.html')

# API routes for dashboard data
@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint to get dashboard statistics"""
    # Prepare filter based on user role
    if current_user.is_admin:
        device_filter = {}
    else:
        device_filter = {'user_id': current_user.id}
    
    # Get device counts
    total_devices = Device.query.filter_by(**device_filter).count()
    online_devices = Device.query.filter_by(status='online', **device_filter).count()
    offline_devices = Device.query.filter_by(status='offline', **device_filter).count()
    
    # Get sensor count
    sensor_count = Sensor.query.join(Device).filter(Device.user_id == current_user.id if not current_user.is_admin else True).count()
    
    # Get reading count from last 24 hours
    day_ago = datetime.utcnow() - timedelta(days=1)
    reading_count = SensorReading.query.join(Sensor).join(Device).filter(
        SensorReading.timestamp > day_ago,
        Device.user_id == current_user.id if not current_user.is_admin else True
    ).count()
    
    # Get device type distribution
    device_types = db.session.query(
        Device.device_type, 
        func.count(Device.id)
    ).filter_by(**device_filter).group_by(Device.device_type).all()
    
    device_type_data = {
        'labels': [t[0] for t in device_types],
        'data': [t[1] for t in device_types]
    }
    
    return jsonify({
        'device_count': {
            'total': total_devices,
            'online': online_devices,
            'offline': offline_devices
        },
        'sensor_count': sensor_count,
        'reading_count': reading_count,
        'device_types': device_type_data
    })

@dashboard_bp.route('/api/recent-activity')
@login_required
def api_recent_activity():
    """API endpoint to get recent device activity"""
    # Set time threshold for recent activity (e.g., last 24 hours)
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    # Prepare filter based on user role
    if current_user.is_admin:
        device_filter = Device.last_seen > time_threshold
    else:
        device_filter = (Device.user_id == current_user.id) & (Device.last_seen > time_threshold)
    
    # Get recent device activity
    recent_devices = Device.query.filter(device_filter).order_by(Device.last_seen.desc()).limit(10).all()
    
    return jsonify([{
        'id': device.id,
        'name': device.name,
        'device_id': device.device_id,
        'status': device.status,
        'last_seen': device.last_seen.isoformat() if device.last_seen else None
    } for device in recent_devices])

@dashboard_bp.route('/api/sensor-data/<int:device_id>')
@login_required
def api_sensor_data(device_id):
    """API endpoint to get sensor data for a device"""
    device = Device.query.get_or_404(device_id)
    
    # Check if user has access to this device
    if not current_user.is_admin and device.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get time range from query parameters (default to last 24 hours)
    hours = request.args.get('hours', 24, type=int)
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Get sensors for this device
    sensors = Sensor.query.filter_by(device_id=device.id).all()
    
    # Prepare data for each sensor
    sensor_data = []
    for sensor in sensors:
        # Get readings for this sensor within time range
        readings = SensorReading.query.filter(
            SensorReading.sensor_id == sensor.id,
            SensorReading.timestamp > time_threshold
        ).order_by(SensorReading.timestamp.asc()).all()
        
        # Format data for chart
        sensor_data.append({
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.sensor_type,
            'unit': sensor.unit,
            'data': {
                'labels': [reading.timestamp.strftime('%Y-%m-%d %H:%M:%S') for reading in readings],
                'values': [reading.value for reading in readings]
            }
        })
    
    return jsonify(sensor_data)

@dashboard_bp.route('/api/device-locations')
@login_required
def api_device_locations():
    """API endpoint to get device locations for map view"""
    # Prepare filter based on user role
    if current_user.is_admin:
        device_filter = Device.location.isnot(None)
    else:
        device_filter = (Device.user_id == current_user.id) & (Device.location.isnot(None))
    
    # Get devices with location information
    devices = Device.query.filter(device_filter).all()
    
    # Extract location data
    location_data = []
    for device in devices:
        # Parse location (assuming format is "latitude,longitude" or similar)
        try:
            lat, lng = device.location.split(',')
            location_data.append({
                'id': device.id,
                'name': device.name,
                'device_id': device.device_id,
                'status': device.status,
                'lat': float(lat.strip()),
                'lng': float(lng.strip())
            })
        except (ValueError, AttributeError):
            # Skip devices with invalid location format
            continue
    
    return jsonify(location_data) 