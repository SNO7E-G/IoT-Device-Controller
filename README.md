# IoT Device Controller

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)
![MQTT](https://img.shields.io/badge/mqtt-paho-orange.svg)

A comprehensive web-based platform for IoT device management, monitoring, and control using Python, Flask, and MQTT.

[Features](#features) •
[Architecture](#architecture) •
[Installation](#installation) •
[Usage](#usage) •
[API Reference](#api-reference) •
[Contributing](#contributing) •
[License](#license)

</div>

## ✨ Features

- **🎛️ Device Control**: Turn IoT devices on/off and adjust settings via a user-friendly web interface
- **📊 Real-Time Monitoring**: View real-time status updates for connected devices using WebSockets
- **🔄 MQTT Integration**: Reliable and efficient device communication via the MQTT protocol
- **🔐 User Authentication**: Secure access with user accounts and role-based permissions
- **📱 Device Management**: Add, remove, configure, and organize your IoT devices
- **📈 Data Visualization**: Display sensor data and device metrics graphically
- **🔔 Alerts and Notifications**: Set up alerts for device status changes or threshold breaches
- **📱 Responsive Design**: Access the controller from any device with a mobile-friendly interface

## 🏗️ Architecture

The system consists of several components:

- **Web Application**: Built with Flask, provides the UI and APIs for device management
- **MQTT Broker**: Handles message passing between the server and IoT devices
- **Database**: Stores device information, user data, and sensor readings
- **Device Simulator**: For testing the system without physical devices


## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- MQTT broker (e.g., Mosquitto)
- SQLite or other database (PostgreSQL/MySQL recommended for production)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/SNO7E-G/IoT-Device-Controller.git
   cd IoT-Device-Controller
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the MQTT broker:
   - See instructions in the [mqtt_broker/README.md](mqtt_broker/README.md) file

5. Create a `.env` file with your configuration:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URI=sqlite:///iot_controller.db
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   MQTT_USERNAME=
   MQTT_PASSWORD=
   ```

## 🖥️ Usage

### Running the Application

1. Initialize the database:
   ```bash
   flask db upgrade
   ```

2. Run the development server:
   ```bash
   python app.py
   ```

3. Access the application at http://localhost:5000

### Testing with the Device Simulator

We provide a device simulator for testing purposes:

```bash
cd device_simulator
python simulator.py --devices 3
```

Options:
- `--devices`: Number of simulated devices to create
- `--types`: Comma-separated list of device types (light,thermostat,switch,sensor)
- `--broker`: MQTT broker address (default: localhost)
- `--port`: MQTT broker port (default: 1883)

## 📂 Project Structure

```
IoT-Device-Controller/
├── app/                      # Application package
│   ├── config/               # Configuration files
│   ├── controllers/          # Route controllers/views
│   ├── models/               # Database models
│   ├── static/               # Static assets (CSS, JS, images)
│   └── templates/            # HTML templates
├── device_simulator/         # Device simulator for testing
├── mqtt_broker/              # MQTT broker configuration
├── docs/                     # Documentation
│   ├── api.md                # API documentation
│   ├── deployment.md         # Deployment guide
│   └── development.md        # Development guide
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 📚 API Reference

The application exposes REST APIs for interacting with devices:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/device/api/devices` | GET | List all devices |
| `/device/api/devices/<id>` | GET | Get device details |
| `/device/api/devices` | POST | Add a new device |
| `/device/api/devices/<id>` | PUT | Update device details |
| `/device/api/devices/<id>` | DELETE | Remove a device |
| `/device/api/devices/<id>/control` | POST | Send command to device |
| `/device/api/devices/<id>/sensors` | GET | Get device sensors |
| `/device/api/sensors/<id>/readings` | GET | Get sensor readings |

See the [full API documentation](docs/api.md) for more details.

## 💻 Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please follow the [development guidelines](docs/development.md) for code style and contribution process.

## 🚀 Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. Set up a reverse proxy with Nginx or Apache

3. Use a secure MQTT broker with authentication

4. Configure a production database (PostgreSQL recommended)

See the [detailed deployment guide](docs/deployment.md) for complete instructions.

## 🔍 Key Features in Detail

### Device Management
The platform allows users to add, view, edit, and delete IoT devices. Each device has properties like name, type, status, location, and configuration settings.

### Real-Time Communication
The system uses MQTT for reliable communication with devices and WebSockets to update the user interface in real-time when device status changes.

### Sensor Readings
Devices can have multiple sensors that send telemetry data. The application stores this data and can display it in charts and graphs for analysis.

### User Authentication and Authorization
The application includes a complete user management system with registration, login, and role-based access control. Regular users can only see and control their own devices, while administrators have access to all devices.


## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Paho MQTT](https://www.eclipse.org/paho/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Eclipse Mosquitto](https://mosquitto.org/)

## 👤 Author

**Mahmoud Ashraf (SNO7E)**

- GitHub: [@SNO7E-G](https://github.com/SNO7E-G)

---

<div align="center">
  <sub>© 2024 Mahmoud Ashraf (SNO7E). All rights reserved.</sub>
</div> 