from datetime import datetime, timezone
from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms.dashboard_forms import DashboardActionForm
from flask_login import login_required, current_user
from app import db

from app.models.user import Role, User
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/manage-users')
@login_required
@role_required(Role.ADMIN)
def manage_users():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars().all()
    return render_template('admin/manage_users.html', users=users)