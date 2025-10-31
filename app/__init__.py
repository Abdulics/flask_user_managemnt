from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import and register blueprints here later
    # from app.routes.auth import auth_bp
    # app.register_blueprint(auth_bp)
    migrate.init_app(app, db)

    # Import your models so Alembic can detect them
    from app.models import user, team, message, address, task, employees, timeoff

    from app.routes.main_route import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    

    return app
