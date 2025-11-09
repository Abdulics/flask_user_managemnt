from datetime import datetime, timezone
from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms.dashboard_forms import DashboardActionForm
from flask_login import login_required, current_user
from app import db

from app.forms.user_forms import UserProfileForm
from app.models.user import Role
from app.utils.decorators import role_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """Render the main dashboard view based on user role."""
   
    # Update last login timestamp
    current_user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    # Route users to their role-specific dashboards
    role = current_user.role.value.lower()

    if role == "admin":
        template = "dashboard/admin_dashboard.html"
    elif role == "manager":
        template = "dashboard/manager_dashboard.html"
    else:
        template = "dashboard/employee_dashboard.html"

    return render_template(template, user=current_user)


# View Profile (Read-only)
@dashboard_bp.route('/profile')
@login_required
def view_profile():
    role = current_user.role.value.lower()

    if role == "admin":
        template = "profile/view_profile_admin.html"
    elif role == "manager":
        template = "profile/view_profile_manager.html"
    else:
        template = "profile/view_profile_employee.html"

    return render_template(template, user=current_user)








