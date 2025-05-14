# app/__init__.py

import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Factory method to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Set secret key from .env or use default for local dev
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_key")
    
    # Register routes from API
    from api.server import register_routes
    register_routes(app)

    return app
