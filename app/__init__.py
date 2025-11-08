from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)


    # Import and register blueprints here later
    # from app.routes.auth import auth_bp
    # app.register_blueprint(auth_bp)
    migrate.init_app(app, db)

    # Import your models so Alembic can detect them
    from app.models import user, team, message, address, task, employees, timeoff, attendance

    from app.routes.main_route import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    return app
