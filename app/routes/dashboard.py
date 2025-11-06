from datetime import datetime, timezone
from flask import Blueprint, render_template, flash, redirect, url_for, request
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



# View Profile (Read-only)
@dashboard_bp.route('/profile')
@login_required
def view_profile():
    return render_template('dashboard/profile_view.html', user=current_user)

# Edit Profile
@dashboard_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UserForm(actor=current_user, target=current_user, obj=current_user)

    if form.validate_on_submit():
        try:
            form.apply_changes(current_user)
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('main.view_profile'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
    elif request.method == 'POST':
        flash("Please correct the errors below.", "warning")

    return render_template('dashboard/profile_edit.html', form=form)



