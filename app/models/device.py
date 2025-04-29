from app.config.database import db
from datetime import datetime
import json

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='offline')
    location = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    mac_address = db.Column(db.String(50))
    firmware_version = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration and metadata stored as JSON
    config = db.Column(db.Text)
    metadata = db.Column(db.Text)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    sensors = db.relationship('Sensor', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, device_id, name, device_type, user_id=None, description=None, 
                 location=None, ip_address=None, mac_address=None, firmware_version=None,
                 config=None, metadata=None):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.user_id = user_id
        self.description = description
        self.location = location
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.firmware_version = firmware_version
        
        # Store configuration and metadata as JSON strings
        self.config = json.dumps(config) if config else '{}'
        self.metadata = json.dumps(metadata) if metadata else '{}'
    
    def get_config(self):
        """Get device configuration as dictionary"""
        try:
            return json.loads(self.config)
        except:
            return {}
    
    def set_config(self, config):
        """Set device configuration from dictionary"""
        self.config = json.dumps(config)
    
    def get_metadata(self):
        """Get device metadata as dictionary"""
        try:
            return json.loads(self.metadata)
        except:
            return {}
    
    def set_metadata(self, metadata):
        """Set device metadata from dictionary"""
        self.metadata = json.dumps(metadata)
    
    def update_status(self, status, timestamp=None):
        """Update device status and last seen time"""
        self.status = status
        if timestamp:
            self.last_seen = timestamp
        else:
            self.last_seen = datetime.utcnow()
    
    def to_dict(self):
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'device_type': self.device_type,
            'description': self.description,
            'status': self.status,
            'location': self.location,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'firmware_version': self.firmware_version,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'config': self.get_config(),
            'metadata': self.get_metadata(),
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Device {self.name} ({self.device_id})>'


class Sensor(db.Model):
    __tablename__ = 'sensors'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20))
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    
    # Relationships
    readings = db.relationship('SensorReading', backref='sensor', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, sensor_id, name, sensor_type, device_id, unit=None, 
                 min_value=None, max_value=None, description=None):
        self.sensor_id = sensor_id
        self.name = name
        self.sensor_type = sensor_type
        self.device_id = device_id
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.description = description
    
    def to_dict(self):
        """Convert sensor to dictionary"""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'name': self.name,
            'sensor_type': self.sensor_type,
            'unit': self.unit,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'description': self.description,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Sensor {self.name} ({self.sensor_id})>'


class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
    
    def __init__(self, value, sensor_id, timestamp=None):
        self.value = value
        self.sensor_id = sensor_id
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        """Convert reading to dictionary"""
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sensor_id': self.sensor_id
        }
    
    def __repr__(self):
        return f'<SensorReading {self.value} at {self.timestamp}>' 