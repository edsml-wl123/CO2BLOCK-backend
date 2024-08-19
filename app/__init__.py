# app/__init__.py
from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    # CORS(app, resources={r"/*": {"origins": "13.55.134.49"}})  # Allow all origins

    # Register routes
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp, url_prefix='/api')

    return app
