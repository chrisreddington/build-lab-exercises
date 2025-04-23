from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined to avoid circular imports
from .category import Category
from .game import Game
from .publisher import Publisher

# Initialize function to be called from app.py
def init_db(app):
    db.init_app(app)
    
    # Create tables when initializing
    with app.app_context():
        db.create_all()