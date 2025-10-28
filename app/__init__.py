from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import and register blueprints here later
    # from app.routes.auth import auth_bp
    # app.register_blueprint(auth_bp)

    return app
