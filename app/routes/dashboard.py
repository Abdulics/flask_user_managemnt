from flask import Blueprint, render_template, flash, redirect, url_for
from app.forms.dashboard_forms import DashboardActionForm
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    print(f"Current user: {current_user.username}")
    form = DashboardActionForm()
    if form.validate_on_submit():
        if form.action.data == 'logout':
            return redirect(url_for('auth.logout'))
        flash(f"Action '{form.action.data}' executed!", "info")
    return render_template('dashboard/dashboard.html', form=form)
