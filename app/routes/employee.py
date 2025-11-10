from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models.user import User

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')   

@employee_bp.route('/profile')
@login_required
def profile():
    return render_template('employee/profile.html')