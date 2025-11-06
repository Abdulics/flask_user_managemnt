from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from app.models.user import User
from ..forms.auth_forms import RegistrationForm, LoginForm
from app import db

# Create the blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----- Routes -----

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # prevent duplicate usernames/emails
        existing = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing:
            flash("A user with that username or email already exists.", "danger")
            return render_template('auth/register.html', form=form)

        user = User(username=form.username.data, email=form.email.data)
        # Password confirmation/validation should be handled by the form validators
        password = form.password.data
        user.password = password  # This will hash the password via the setter

        # Here you would normally add the user to the database
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return render_template('auth/register.html', form=form)
            

        flash(f"Account created for {user.username}! Please log in.", "success")
        return redirect(url_for('auth.login'))  # redirect to login page
    # GET request or validation failed
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = getattr(form, 'username_or_email', None)
        if username_or_email is not None:
            identifier = username_or_email.data
        else:
            # fallback if your form uses separate fields
            identifier = getattr(form, 'username', None)
            identifier = (identifier.data if identifier else None) or getattr(form, 'email', None).data

        # Here you would normally check credentials
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Logged in as {identifier}", "success")
            return redirect(url_for('dashboard.index'))  # redirect to dashboard
        else:
            flash("Invalid username/email or password.", "danger")

    # GET request or validation failed
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    # Here you would normally handle logout logic
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))  # redirect to landing page


