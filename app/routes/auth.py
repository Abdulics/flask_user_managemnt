from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user

from app.forms.register_form import RegisterForm
from app.models.employees import Employee
from app.models.user import User
from app import db

# Create the blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

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
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
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
