#!/usr/bin/env python3
"""
IoT Device Simulator for testing the IoT Device Controller

This script simulates one or more IoT devices connecting to the MQTT broker,
receiving commands, and publishing telemetry data.
"""

import json
import time
import random
import argparse
import logging
import signal
import sys
from datetime import datetime
from uuid import uuid4

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('device_simulator')

# Define device types and their capabilities
DEVICE_TYPES = {
    'light': {
        'commands': ['power', 'set_brightness', 'set_color', 'status'],
        'telemetry': ['power_state', 'brightness', 'color', 'power_usage'],
        'config': {
            'min_brightness': 0,
            'max_brightness': 100,
            'supports_color': True
        }
    },
    'thermostat': {
        'commands': ['power', 'set_temperature', 'set_mode', 'status'],
        'telemetry': ['power_state', 'current_temperature', 'target_temperature', 'humidity', 'mode'],
        'config': {
            'min_temperature': 16,
            'max_temperature': 30,
            'modes': ['auto', 'heat', 'cool', 'off']
        }
    },
    'switch': {
        'commands': ['power', 'status'],
        'telemetry': ['power_state', 'power_usage'],
        'config': {}
    },
    'sensor': {
        'commands': ['status', 'calibrate'],
        'telemetry': ['temperature', 'humidity', 'pressure', 'battery_level'],
        'config': {
            'reporting_interval': 60,  # seconds
        }
    }
}

class IoTDevice:
    """Simulated IoT device that connects to MQTT and responds to commands"""
    
    def __init__(self, device_id, device_type, name, broker_host='localhost', broker_port=1883, username=None, password=None):
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        
        if device_type not in DEVICE_TYPES:
            raise ValueError(f"Unknown device type: {device_type}")
        
        self.capabilities = DEVICE_TYPES[device_type]
        self.state = self._init_state()
        
        # Set up MQTT client
        self.client = mqtt.Client(client_id=f"simulator_{device_id}")
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set up MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Connect to broker
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.connected = False
        
        # Telemetry settings
        self.telemetry_interval = self.capabilities['config'].get('reporting_interval', 30)
        self.last_telemetry = 0
        
        # Flag to control the device loop
        self.running = False
    
    def _init_state(self):
        """Initialize device state based on device type"""
        state = {
            'status': 'online',
            'last_seen': datetime.utcnow().isoformat()
        }
        
        if self.device_type == 'light':
            state.update({
                'power_state': 'off',
                'brightness': 50,
                'color': '#ffffff',
                'power_usage': 0.0
            })
        elif self.device_type == 'thermostat':
            state.update({
                'power_state': 'off',
                'current_temperature': 22.0,
                'target_temperature': 22.0,
                'humidity': 40,
                'mode': 'off'
            })
        elif self.device_type == 'switch':
            state.update({
                'power_state': 'off',
                'power_usage': 0.0
            })
        elif self.device_type == 'sensor':
            state.update({
                'temperature': 22.0,
                'humidity': 40,
                'pressure': 1013.25,
                'battery_level': 100
            })
        
        return state
    
    def connect(self):
        """Connect to the MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            self.running = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        logger.info(f"Device {self.device_id} disconnecting")
        self.running = False
        
        # Send offline status
        self.state['status'] = 'offline'
        self.state['last_seen'] = datetime.utcnow().isoformat()
        self.publish_status()
        
        self.client.loop_stop()
        self.client.disconnect()
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info(f"Device {self.device_id} connected to MQTT broker")
            self.connected = True
            
            # Subscribe to command topic
            command_topic = f"devices/{self.device_id}/command"
            self.client.subscribe(command_topic)
            logger.info(f"Subscribed to {command_topic}")
            
            # Publish initial status
            self.publish_status()
        else:
            logger.error(f"Failed to connect to MQTT broker with result code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        logger.info(f"Device {self.device_id} disconnected from MQTT broker with result code {rc}")
        self.connected = False
        
        # Try to reconnect if this was unexpected
        if rc != 0 and self.running:
            logger.info("Attempting to reconnect...")
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received from the broker"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on {topic}: {payload}")
            
            # Handle command
            if topic == f"devices/{self.device_id}/command":
                self._handle_command(payload)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _handle_command(self, payload):
        """Handle a command received from the broker"""
        command = payload.get('command')
        params = payload.get('params', {})
        
        if command not in self.capabilities['commands']:
            logger.warning(f"Received unsupported command: {command}")
            self._publish_response(command, False, f"Command '{command}' not supported by this device")
            return
        
        # Handle supported commands
        if command == 'status':
            # Just return current status
            self._publish_response(command, True, "Status retrieved successfully")
        
        elif command == 'power':
            state = params.get('state', 'toggle')
            
            if state == 'toggle':
                new_state = 'on' if self.state.get('power_state') == 'off' else 'off'
            else:
                new_state = state
            
            self.state['power_state'] = new_state
            
            # Update power usage based on state
            if new_state == 'on':
                if self.device_type == 'light':
                    # Power usage proportional to brightness
                    self.state['power_usage'] = round(0.1 * self.state.get('brightness', 100) / 100, 2)
                elif self.device_type == 'switch':
                    self.state['power_usage'] = round(random.uniform(0.5, 2.0), 2)
                elif self.device_type == 'thermostat':
                    # More power if heating/cooling
                    if self.state.get('mode') != 'off':
                        self.state['power_usage'] = round(random.uniform(1.0, 3.0), 2)
            else:
                self.state['power_usage'] = 0.0
            
            self._publish_response(command, True, f"Power set to {new_state}")
        
        elif command == 'set_brightness':
            brightness = int(params.get('brightness', 50))
            min_brightness = self.capabilities['config'].get('min_brightness', 0)
            max_brightness = self.capabilities['config'].get('max_brightness', 100)
            
            # Ensure brightness is within range
            brightness = max(min_brightness, min(brightness, max_brightness))
            self.state['brightness'] = brightness
            
            # Update power usage if light is on
            if self.state.get('power_state') == 'on':
                self.state['power_usage'] = round(0.1 * brightness / 100, 2)
            
            self._publish_response(command, True, f"Brightness set to {brightness}")
        
        elif command == 'set_color':
            color = params.get('color', '#ffffff')
            
            # Validate color format (simple check)
            if color.startswith('#') and len(color) in [4, 7]:
                self.state['color'] = color
                self._publish_response(command, True, f"Color set to {color}")
            else:
                self._publish_response(command, False, "Invalid color format")
        
        elif command == 'set_temperature':
            temperature = float(params.get('temperature', 22.0))
            min_temp = self.capabilities['config'].get('min_temperature', 16)
            max_temp = self.capabilities['config'].get('max_temperature', 30)
            
            # Ensure temperature is within range
            temperature = max(min_temp, min(temperature, max_temp))
            self.state['target_temperature'] = temperature
            
            # Simulate thermostat behavior - gradually move current_temperature towards target
            # This will be handled in the run loop
            
            self._publish_response(command, True, f"Temperature set to {temperature}")
        
        elif command == 'set_mode':
            mode = params.get('mode', 'auto')
            supported_modes = self.capabilities['config'].get('modes', ['auto', 'off'])
            
            if mode in supported_modes:
                self.state['mode'] = mode
                self._publish_response(command, True, f"Mode set to {mode}")
            else:
                self._publish_response(command, False, f"Mode {mode} not supported")
        
        elif command == 'calibrate':
            # Simulate sensor calibration
            offset = float(params.get('offset', 0.0))
            self.state['temperature'] += offset
            self._publish_response(command, True, f"Sensor calibrated with offset {offset}")
        
        # Update status after command
        self.publish_status()
    
    def _publish_response(self, command, success, message):
        """Publish a response to a command"""
        response_topic = f"devices/{self.device_id}/response"
        payload = {
            'command': command,
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.client.publish(response_topic, json.dumps(payload))
        logger.info(f"Published response: {payload}")
    
    def publish_status(self):
        """Publish device status"""
        status_topic = f"devices/{self.device_id}/status"
        self.state['last_seen'] = datetime.utcnow().isoformat()
        
        self.client.publish(status_topic, json.dumps(self.state))
        logger.info(f"Published status for {self.device_id}")
    
    def publish_telemetry(self):
        """Publish telemetry data"""
        telemetry_topic = f"devices/{self.device_id}/telemetry"
        
        # Prepare telemetry data
        telemetry = {
            'timestamp': datetime.utcnow().isoformat(),
            'readings': {}
        }
        
        # Add relevant readings based on device type
        if self.device_type == 'light':
            telemetry['readings'] = {
                'power_state': self.state['power_state'],
                'brightness': self.state['brightness'],
                'power_usage': self.state['power_usage']
            }
        elif self.device_type == 'thermostat':
            telemetry['readings'] = {
                'power_state': self.state['power_state'],
                'current_temperature': self.state['current_temperature'],
                'target_temperature': self.state['target_temperature'],
                'humidity': self.state['humidity'],
                'mode': self.state['mode']
            }
        elif self.device_type == 'switch':
            telemetry['readings'] = {
                'power_state': self.state['power_state'],
                'power_usage': self.state['power_usage']
            }
        elif self.device_type == 'sensor':
            telemetry['readings'] = {
                'temperature': self.state['temperature'],
                'humidity': self.state['humidity'],
                'pressure': self.state['pressure'],
                'battery_level': self.state['battery_level']
            }
        
        self.client.publish(telemetry_topic, json.dumps(telemetry))
        logger.info(f"Published telemetry for {self.device_id}")
    
    def update_simulated_values(self):
        """Update simulated values for sensors and devices"""
        now = time.time()
        
        # Sensor values drift randomly
        if self.device_type == 'sensor':
            self.state['temperature'] += random.uniform(-0.1, 0.1)
            self.state['humidity'] += random.uniform(-0.5, 0.5)
            self.state['humidity'] = max(0, min(100, self.state['humidity']))
            self.state['pressure'] += random.uniform(-0.1, 0.1)
            
            # Battery level slowly decreases
            if random.random() < 0.1:  # 10% chance each update
                self.state['battery_level'] = max(0, self.state['battery_level'] - 0.1)
        
        # Thermostat simulation - current temperature moves towards target
        elif self.device_type == 'thermostat':
            current_temp = self.state['current_temperature']
            target_temp = self.state['target_temperature']
            
            if self.state['power_state'] == 'on' and self.state['mode'] != 'off':
                # Move towards target temperature
                if current_temp < target_temp:
                    self.state['current_temperature'] += min(0.2, target_temp - current_temp)
                elif current_temp > target_temp:
                    self.state['current_temperature'] -= min(0.2, current_temp - target_temp)
            else:
                # Drift towards ambient room temperature (assumed to be 21°C)
                ambient = 21.0
                if current_temp < ambient:
                    self.state['current_temperature'] += min(0.1, ambient - current_temp)
                elif current_temp > ambient:
                    self.state['current_temperature'] -= min(0.1, current_temp - ambient)
            
            # Humidity fluctuates
            self.state['humidity'] += random.uniform(-1, 1)
            self.state['humidity'] = max(20, min(70, self.state['humidity']))
    
    def run(self):
        """Main device loop"""
        logger.info(f"Device {self.device_id} ({self.device_type}) running")
        self.last_telemetry = time.time()
        
        while self.running:
            now = time.time()
            
            # Update simulated values
            self.update_simulated_values()
            
            # Publish telemetry at the specified interval
            if now - self.last_telemetry >= self.telemetry_interval:
                if self.connected:
                    self.publish_telemetry()
                self.last_telemetry = now
            
            # Sleep to avoid high CPU usage
            time.sleep(1)

def create_device(device_type, broker_host, broker_port, mqtt_username=None, mqtt_password=None):
    """Create a new simulated device"""
    device_id = str(uuid4())
    name = f"{device_type.capitalize()} {device_id[:6]}"
    
    device = IoTDevice(
        device_id=device_id,
        device_type=device_type,
        name=name,
        broker_host=broker_host,
        broker_port=broker_port,
        username=mqtt_username,
        password=mqtt_password
    )
    
    return device

def main():
    """Main function to run the simulator"""
    parser = argparse.ArgumentParser(description='IoT Device Simulator')
    parser.add_argument('--broker', type=str, default='localhost', help='MQTT broker hostname')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--username', type=str, help='MQTT username')
    parser.add_argument('--password', type=str, help='MQTT password')
    parser.add_argument('--devices', type=int, default=1, help='Number of devices to simulate')
    parser.add_argument('--types', type=str, default='light,thermostat,switch,sensor', 
                        help='Comma-separated list of device types to simulate')
    args = parser.parse_args()
    
    # Parse device types
    device_types = args.types.split(',')
    
    # Create devices
    devices = []
    for i in range(args.devices):
        device_type = random.choice(device_types)
        try:
            device = create_device(
                device_type=device_type,
                broker_host=args.broker,
                broker_port=args.port,
                mqtt_username=args.username,
                mqtt_password=args.password
            )
            
            success = device.connect()
            if success:
                devices.append(device)
                logger.info(f"Created {device_type} device: {device.device_id} ({device.name})")
            else:
                logger.error(f"Failed to connect device {device.device_id}")
        except Exception as e:
            logger.error(f"Error creating device: {e}")
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Simulator shutting down...")
        for device in devices:
            device.disconnect()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start device loops
    try:
        # Create and start threads for each device
        for device in devices:
            device.run()
    except Exception as e:
        logger.error(f"Simulator error: {e}")
    finally:
        # Ensure all devices are properly disconnected
        for device in devices:
            device.disconnect()

if __name__ == "__main__":
    main() 