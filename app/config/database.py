from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app"""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all() 