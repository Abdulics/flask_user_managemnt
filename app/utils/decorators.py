from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                flash("You don’t have permission to view this page.", "danger")
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return wrapper
    return decorator