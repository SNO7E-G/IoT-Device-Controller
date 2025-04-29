# MQTT Broker Setup

This directory contains configuration for setting up a local MQTT broker for the IoT Device Controller.

## Option 1: Use Mosquitto in Docker

The easiest way to get started is to use the Eclipse Mosquitto broker in a Docker container.

### Prerequisites

- Docker installed on your system

### Start the broker

Run the following command from the project root:

```bash
docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto
```

For persistence and custom configuration:

```bash
docker run -it -p 1883:1883 -p 9001:9001 \
  -v $(pwd)/mqtt_broker/config:/mosquitto/config \
  -v $(pwd)/mqtt_broker/data:/mosquitto/data \
  -v $(pwd)/mqtt_broker/log:/mosquitto/log \
  eclipse-mosquitto
```

## Option 2: Install Mosquitto directly

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
sudo systemctl start mosquitto.service
```

### Windows

1. Download the installer from [https://mosquitto.org/download/](https://mosquitto.org/download/)
2. Run the installer and follow the instructions
3. Start the service from the Windows Services panel

### MacOS

```bash
brew install mosquitto
```

To start mosquitto manually:

```bash
mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf
```

To have it start automatically:

```bash
brew services start mosquitto
```

## Basic Configuration

Create a file named `mosquitto.conf` in the `mqtt_broker/config` directory with the following content:

```
# Default listener
listener 1883

# WebSockets listener
listener 9001
protocol websockets

# Allow anonymous connections (for development only)
allow_anonymous true

# Persistence
persistence true
persistence_location /mosquitto/data/
```

For production use, you should set up authentication. Add the following lines to your configuration:

```
# Disable anonymous access
allow_anonymous false

# Password file
password_file /mosquitto/config/passwd
```

Then create a password file:

```bash
# Create a password file with a user
mosquitto_passwd -c /path/to/passwd username
```

## Testing the Connection

You can test your MQTT broker connection using the mosquitto command line clients:

```bash
# Subscribe to a topic
mosquitto_sub -h localhost -t "test/topic" -v

# Publish to a topic
mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT"
```

## Using with IoT Device Controller

Configure your IoT Device Controller to connect to this broker by setting these environment variables:

```
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=your_username  # if using authentication
MQTT_PASSWORD=your_password  # if using authentication
```

## Security Considerations

For production deployments, consider:

1. Using TLS/SSL for encrypted connections
2. Setting up proper authentication
3. Implementing access control lists
4. Putting the broker behind a firewall
5. Regularly updating the broker software 