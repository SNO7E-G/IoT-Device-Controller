import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
from flask import current_app
from flask_socketio import emit

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', 60))
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'iot_controller_server')

# Create MQTT client
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)

# Set username and password if provided
if MQTT_USERNAME and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    print(f"Connected to MQTT broker with result code {rc}")
    
    # Subscribe to topics
    client.subscribe("devices/+/status")
    client.subscribe("devices/+/telemetry")
    client.subscribe("devices/+/response")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        handle_mqtt_message(topic, payload)
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def handle_mqtt_message(topic, payload):
    """Process incoming MQTT messages"""
    # Extract device ID from topic
    topic_parts = topic.split('/')
    if len(topic_parts) >= 3:
        device_id = topic_parts[1]
        message_type = topic_parts[2]
        
        # Update device status in database if it's a status message
        if message_type == 'status':
            from app.models.device import Device
            from app.config.database import db
            
            with current_app.app_context():
                device = Device.query.filter_by(device_id=device_id).first()
                if device:
                    device.status = payload.get('status', 'offline')
                    device.last_seen = payload.get('timestamp')
                    db.session.commit()
        
        # Emit message to connected clients via WebSocket
        if message_type in ['status', 'telemetry', 'response']:
            socketio_event = f"device_{message_type}"
            emit(socketio_event, {'device_id': device_id, 'data': payload}, namespace='/', broadcast=True)

def publish_command(device_id, command, params=None):
    """Publish a command to a device"""
    if params is None:
        params = {}
    
    topic = f"devices/{device_id}/command"
    payload = {
        "command": command,
        "params": params
    }
    
    mqtt_client.publish(topic, json.dumps(payload))
    return True

# Set up callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Try to connect to broker
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    mqtt_client.loop_start()  # Start network loop in background thread
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")

def get_mqtt_client():
    """Return the MQTT client instance"""
    return mqtt_client 