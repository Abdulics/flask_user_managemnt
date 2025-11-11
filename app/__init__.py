import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

@click.command(name='init-db')
@with_appcontext
def init_db_command():
    from app.models.user import User, Role
    from app.models.employees import Employee
    from app.models.department import Department
    from datetime import date

    db.create_all()
    if not User.query.filter_by(username='admin').first():
        # create admin user same as before
        click.echo("Creating default admin user...")
        admin_dept = Department(name='Administration', description='Administrative Department')
        db.session.add(admin_dept)
        db.session.commit()

        admin_employee = Employee(
            first_name='Admin',
            last_name='User',
            email='admin@teammanager.com',
            phone='555-0000',
            position='System Administrator',
            hire_date=date.today(),
            department_id=admin_dept.id
            )
        db.session.add(admin_employee)
        db.session.commit()

        admin_user = User(
            username='admin',
            email='admin@teammanager.com',
            role=Role.ADMIN,
            employee_id=admin_employee.id
            )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("")
        click.echo("Admin user created successfully!")
    else:
        click.echo("Admin already exists. Skipping creation.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf = CSRFProtect(app)

    db.init_app(app)
    csrf.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = 'Please log in to access this page.'

    app.cli.add_command(init_db_command)
    migrate.init_app(app, db)

    # Import your models so Alembic can detect them
    from app.models import user, team, message, address, task, employees, timeoff, attendance, department

    from app.routes.main_route import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from app.routes.manager import manager_bp
    app.register_blueprint(manager_bp)

    from app.routes.employee import employee_bp
    app.register_blueprint(employee_bp)

    from app.routes.messages import message_bp
    app.register_blueprint(message_bp)
    
    from app.routes.tasks import task_bp
    app.register_blueprint(task_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    return app
