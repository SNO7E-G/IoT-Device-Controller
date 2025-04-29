# Development Guide

This guide provides information for developers who want to contribute to the IoT Device Controller project.

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Visual Studio Code (recommended) or any IDE of your choice
- MQTT broker (e.g., Mosquitto) for local testing

### Setting Up Your Development Environment

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/your-username/IoT-Device-Controller.git
   cd IoT-Device-Controller
   ```

2. **Create a Virtual Environment**

   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pylint black
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the project root:

   ```
   SECRET_KEY=dev_secret_key
   DATABASE_URI=sqlite:///iot_controller_dev.db
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   MQTT_USERNAME=
   MQTT_PASSWORD=
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

5. **Initialize the Database**

   ```bash
   flask db upgrade
   ```

6. **Run the Development Server**

   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`.

## Project Structure

Understanding the project structure is essential for effective development:

```
IoT-Device-Controller/
├── app/                      # Main application package
│   ├── config/               # Configuration modules
│   │   ├── database.py       # Database configuration
│   │   └── mqtt_client.py    # MQTT client setup
│   ├── controllers/          # Route controllers
│   │   ├── auth_controller.py # Authentication routes
│   │   ├── dashboard_controller.py # Dashboard routes
│   │   └── device_controller.py # Device management routes
│   ├── models/               # Database models
│   │   ├── device.py         # Device and sensor models
│   │   └── user.py           # User model
│   ├── static/               # Static assets
│   │   ├── css/              # Stylesheets
│   │   ├── js/               # JavaScript files
│   │   └── images/           # Image assets
│   └── templates/            # HTML templates
│       ├── auth/             # Authentication templates
│       ├── dashboard/        # Dashboard templates
│       └── device/           # Device management templates
├── device_simulator/         # Device simulator for testing
├── mqtt_broker/              # MQTT broker configuration
├── tests/                    # Test suite
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Development Workflow

### Branching Strategy

We follow a simplified Git Flow approach:

- `main`: Production-ready code
- `develop`: Integration branch for feature development
- `feature/<feature-name>`: For new features
- `fix/<bug-name>`: For bug fixes
- `release/<version>`: For release preparation

### Creating a New Feature

1. **Create a feature branch**

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests to ensure everything works**

   ```bash
   pytest
   ```

4. **Commit your changes with meaningful messages**

   ```bash
   git add .
   git commit -m "feat: Add your meaningful commit message"
   ```

5. **Push your branch and create a Pull Request**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a Pull Request on GitHub targeting the `develop` branch.

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Routine tasks, maintenance, etc.

Example: `feat: Add temperature sensor support`

## Code Standards

### Python Style Guide

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code with some modifications:

- Use 4 spaces for indentation
- Maximum line length is 100 characters
- Use docstrings for all classes and functions
- Use type hints where appropriate
- Use f-strings for string formatting

### JavaScript Style Guide

For JavaScript code, we follow a simplified version of the Airbnb JavaScript Style Guide:

- Use camelCase for variable and function names
- Use PascalCase for classes and constructor functions
- Use 2 spaces for indentation
- Use semicolons at the end of statements
- Use ES6 features where appropriate

### HTML/CSS Style Guide

- Use 2 spaces for indentation
- Use lowercase for HTML element names and attributes
- Use kebab-case for CSS class names

### Code Formatting

We use the following tools for code formatting:

- **Python**: [Black](https://black.readthedocs.io/) with a line length of 100
  ```bash
  black --line-length 100 app/
  ```

- **JavaScript**: [ESLint](https://eslint.org/) with the Airbnb configuration
  ```bash
  npm run lint
  ```

### Code Documentation

All code should be properly documented:

- **Python**: Use docstrings for all classes and functions
  ```python
  def calculate_average(values):
      """
      Calculate the average of a list of values.
      
      Args:
          values (list): A list of numerical values
          
      Returns:
          float: The average of the values
          
      Raises:
          ValueError: If the list is empty
      """
      if not values:
          raise ValueError("Cannot calculate average of empty list")
      return sum(values) / len(values)
  ```

- **JavaScript**: Use JSDoc comments for functions and classes
  ```javascript
  /**
   * Calculate the average of an array of values
   * @param {Array<number>} values - The values to average
   * @returns {number} The average value
   * @throws {Error} If the array is empty
   */
  function calculateAverage(values) {
    if (values.length === 0) {
      throw new Error('Cannot calculate average of empty array');
    }
    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }
  ```

## Testing

### Running Tests

We use [pytest](https://docs.pytest.org/) for testing Python code:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_device_controller.py
```

### Writing Tests

Tests should be organized according to the application structure:

- `tests/unit/`: Unit tests for individual functions and classes
- `tests/integration/`: Tests for interactions between components
- `tests/functional/`: End-to-end tests for API endpoints

Example unit test:

```python
# tests/unit/test_device_model.py
import pytest
from app.models.device import Device

def test_device_status_update():
    device = Device(device_id="test123", name="Test Device", device_type="sensor")
    device.update_status("online")
    assert device.status == "online"
    assert device.last_seen is not None
```

### Test Coverage

Aim for at least 80% test coverage for new code. Use the coverage report to identify untested code:

```bash
pytest --cov=app tests/ --cov-report=html
```

## Working with the Database

### Database Migrations

We use Flask-Migrate for database migrations:

```bash
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Revert migrations
flask db downgrade
```

### Database Seeding

For development and testing, you can seed the database with sample data:

```bash
# Create seed data in the database
python -m app.scripts.seed_database
```

## Working with MQTT

### Local MQTT Testing

1. **Install Mosquitto**:
   - Windows: Download from [mosquitto.org](https://mosquitto.org/download/)
   - Linux: `sudo apt install mosquitto mosquitto-clients`
   - macOS: `brew install mosquitto`

2. **Start Mosquitto** (if not running as a service):
   ```bash
   mosquitto -v
   ```

3. **Subscribe to a test topic** (in a separate terminal):
   ```bash
   mosquitto_sub -t "devices/+/status"
   ```

4. **Publish a test message** (in another terminal):
   ```bash
   mosquitto_pub -t "devices/test123/status" -m '{"status": "online", "timestamp": "2023-01-01T12:00:00Z"}'
   ```

### Debugging MQTT

To debug MQTT communication issues:

1. Enable verbose logging in the MQTT broker
2. Use the MQTT Explorer tool to visualize message flow
3. Check the application logs for MQTT client errors

## Logging

We use Python's built-in logging module. Log messages should be descriptive and include relevant context:

```python
import logging

logger = logging.getLogger(__name__)

def process_device_command(device_id, command):
    logger.info(f"Processing command '{command}' for device {device_id}")
    try:
        # Process command
        result = execute_command(device_id, command)
        logger.debug(f"Command result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing command '{command}' for device {device_id}: {str(e)}")
        raise
```

## Debugging

### Debug Mode

When running in development, set `FLASK_DEBUG=1` in your `.env` file to enable Flask's debug mode.

### Debug Tools

- **Flask Debug Toolbar**: Enabled in development for request inspection
- **Python Debugger (pdb)**: Use in your code to set breakpoints:
  ```python
  import pdb; pdb.set_trace()
  ```
- **VS Code Debugging**: Configure `.vscode/launch.json` for integrated debugging

## Continuous Integration

We use GitHub Actions for CI/CD. When you push changes or create a pull request:

1. Tests are automatically run
2. Code linting is performed
3. Test coverage is calculated

The CI pipeline is defined in `.github/workflows/ci.yml`.

## Release Process

For project maintainers, the release process is as follows:

1. **Prepare Release**:
   - Create a release branch: `git checkout -b release/vX.Y.Z`
   - Update version numbers and update CHANGELOG.md
   - Final testing and bug fixes

2. **Finalize Release**:
   - Merge release branch to main: `git checkout main && git merge --no-ff release/vX.Y.Z`
   - Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   - Push to GitHub: `git push origin main --tags`

3. **Update Development Branch**:
   - Merge main back to develop: `git checkout develop && git merge --no-ff main`
   - Push to GitHub: `git push origin develop`

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MQTT Protocol Documentation](https://mqtt.org/mqtt-specification/)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)

---

© 2024 Mahmoud Ashraf (SNO7E). All rights reserved. 