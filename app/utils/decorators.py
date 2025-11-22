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

            if not current_user.employee:
                flash("Your account is missing an employee record. Please contact HR/admin.", "danger")
                return redirect(url_for('main.dashboard'))

            if current_user.employee.role not in roles:
                allowed = ", ".join(r.value.capitalize() for r in roles)
                flash(f"Access denied. This page is for: {allowed}.", "danger")
                return redirect(url_for('main.dashboard'))

            return f(*args, **kwargs)
        return wrapper
    return decorator
