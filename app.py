from flask import Flask, render_template, redirect, url_for, flash, request
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import application modules
from app.models.user import User
from app.models.device import Device
from app.controllers.auth_controller import auth_bp
from app.controllers.device_controller import device_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.config.database import init_db, db

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_change_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///iot_controller.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
socketio = SocketIO(app)
init_db(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(device_bp)
app.register_blueprint(dashboard_bp)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# MQTT connection and event handlers
from app.config.mqtt_client import mqtt_client, handle_mqtt_message

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        print(f"User {current_user.username} connected")

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        print(f"User {current_user.username} disconnected")

# Run the application
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True) 