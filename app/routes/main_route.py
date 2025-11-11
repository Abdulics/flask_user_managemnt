from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Route users to their role-specific dashboards
    role = current_user.employee.role.value.lower()

    if role == "admin":
        return redirect(url_for('admin.admin_dashboard'))
    elif role == "manager":
        return redirect(url_for('manager.manager_dashboard'))
    else:
        return redirect(url_for('employee.employee_dashboard'))