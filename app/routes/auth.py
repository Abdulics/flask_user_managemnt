from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..forms.auth_forms import RegistrationForm, LoginForm

# Create the blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')

# ----- Routes -----

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        # Password confirmation/validation should be handled by the form validators
        password = form.password.data

        # Here you would normally create a user in the DB
        flash(f"User {username} registered successfully!", "success")
        print(f"Registered user: {username}, Email: {email}")
        return redirect(url_for('auth.login'))

    # GET request or validation failed
    return render_template('register.html', form=form)


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
        flash(f"Logged in as {identifier}", "success")
        print(f"User logged in: {identifier}")
        return redirect(url_for('landing_page.index'))  # redirect to landing/home page

    # GET request or validation failed
    return render_template('login.html', form=form)
