from datetime import datetime, timezone
from flask import Blueprint, render_template, flash, redirect, url_for
from app.forms.dashboard_forms import DashboardActionForm
from flask_login import login_required, current_user
from app import db

from app.forms.user_forms import UserForm

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    print(f"Current user: {current_user.username}")
    """Set last_login to now (useful after successful auth)."""
    current_user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    form = DashboardActionForm()
    if form.validate_on_submit():
        if form.action.data == 'logout':
            return redirect(url_for('auth.logout'))
        flash(f"Action '{form.action.data}' executed!", "info")
    return render_template('dashboard/dashboard.html', form=form)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserForm(actor=current_user, target=current_user, obj=current_user)
    print(f"Editing profile for user: {current_user.username}")
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash("Profile updated successfully!", "success")
    return render_template('dashboard/profile.html', form=form)

