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

# Edit Profile
@dashboard_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Allow users to edit their own profile.
    - Users can edit username and email if not admin/manager.
    - Role can only be changed by an admin; admin cannot change their own role.
    - Password is handled separately, so ignored here.
    """
    # Bind form to current user
    form = UserProfileForm(actor=current_user, target=current_user, obj=current_user)

    print(f"Editing profile for user: {current_user.username}")
    print(f"Form fields: {form._fields.keys()}")
    print(f"Form data on POST: {request.form}")

    # Ignore password in this form
    if form.password.data:
        print("Password field should be ignored here.")

    if form.validate_on_submit():
        try:
            # Apply changes from form to the user object
            form.apply_changes(current_user)
            db.session.commit()
            flash("Profile updated successfully!", "success")
            # Redirect to the appropriate profile view based on role
            role = current_user.role.value.lower()
            if role == "admin":
                return redirect(url_for('dashboard.view_profile_admin'))
            elif role == "manager":
                return redirect(url_for('dashboard.view_profile_manager'))
            else:
                return redirect(url_for('dashboard.view_profile_employee'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
    elif request.method == 'POST':
        flash("Please correct the errors below.", "warning")

    return render_template('dashboard/profile_edit.html', form=form)






