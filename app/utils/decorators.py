from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Accepts one or more roles.
    Example: @role_required(Role.ADMIN, Role.MANAGER)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for('auth.login'))

            # Ensure employee exists
            if not current_user.employee:
                flash("You don’t have permission to view this page.", "danger")
                return redirect(url_for('main.dashboard'))

            # Allow if current role is in the allowed roles
            if current_user.employee.role not in roles:
                flash("You don’t have permission to view this page.", "danger")
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return wrapper
    return decorator
