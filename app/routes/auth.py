from flask import Blueprint, render_template, request, redirect, url_for, flash

# Create the blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')

# ----- Routes -----

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Grab form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Simple validation (expand later)
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.register'))

        # Here you would normally create a user in the DB
        flash(f"User {username} registered successfully!", "success")
        return redirect(url_for('auth.login'))

    # GET request
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')

        # Here you would normally check credentials
        flash(f"Logged in as {username_or_email}", "success")
        return redirect(url_for('landing_page.index'))  # redirect to landing/home page

    # GET request
    return render_template('login.html')
