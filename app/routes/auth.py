from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urljoin, urlparse

from app.forms.register_form import RegisterForm
from app.models.employees import Employee
from app.models.user import User
from app import db

# Create the blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _is_safe_redirect(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                next_page = request.args.get('next')
                if _is_safe_redirect(next_page):
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Your account has been deactivated. Please contact admin.', 'danger')
        else:
            flash('Invalid username/email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if employee exists
        employee = Employee.query.filter_by(email=email).first()
        if not employee:
            flash('No employee record found with this email. Please contact admin.', 'danger')
            return render_template('auth/register.html', form=form)

        # Check if user already exists
        if employee.user:
            flash('An account already exists for this email.', 'danger')
            return render_template('auth/register.html', form=form)

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html', form=form)

        # Create the user
        user = User(
            username=username,
            email=email,
            employee_id=employee.id
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password') or ''
        new_password = request.form.get('new_password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('employee.profile'))

    return render_template('auth/change_password.html')
