from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize database
    init_db(app)

    # Register routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app