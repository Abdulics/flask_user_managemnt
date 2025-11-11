from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import Role, User
from app.utils.decorators import role_required

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/view')
@login_required
def view_profile():
    role = current_user.role.value.lower()
    template = f"profile/view_profile_{role}.html"
    return render_template(template, user=current_user, form=None)

# User editing their own profile
@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    target_user = current_user
    return handle_edit_profile(target_user)

# Admin editing any profile
@profile_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN)  # Custom decorator that checks current_user.role
def edit_user_profile(user_id):
    target_user = User.query.get_or_404(user_id)
    return handle_edit_profile(target_user)

# Shared logic
def handle_edit_profile(target_user):
    form = UserProfileForm(obj=target_user, actor=current_user)
    
    if request.method == 'GET':
        form.username.data = target_user.username
        form.email.data = target_user.email
        form.bio.data = target_user.bio
        form.is_active.data = target_user.is_active

        if hasattr(form, "role"):
            form.role.data = target_user.role.name

        # Employee fields
        if getattr(target_user, "employee", None):
            form.employee_id.data = target_user.employee.employee_id
            form.first_name.data = target_user.employee.first_name
            form.last_name.data = target_user.employee.last_name
            form.department.data = target_user.employee.department
            form.position.data = target_user.employee.position
            form.hire_date.data = target_user.employee.hire_date
            form.salary.data = target_user.employee.salary
            form.manager_id.data = target_user.employee.manager_id


    if form.validate_on_submit():
        # Save user and employee fields according to permissions
        form.apply_changes(target_user)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/edit_profile.html', form=form, user=target_user)



