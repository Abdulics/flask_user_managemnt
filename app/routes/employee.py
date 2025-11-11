from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')   
from app.models.task import Task

@employee_bp.route('/dashboard')
@login_required
def employee_dashboard():
    my_tasks = Task.query.filter_by(assigned_to_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()
    pending_tasks = Task.query.filter_by(assigned_to_id=current_user.id, status='pending').count()
    in_progress_tasks = Task.query.filter_by(assigned_to_id=current_user.id, status='in_progress').count()
    completed_tasks = Task.query.filter_by(assigned_to_id=current_user.id, status='completed').count()
    
    return render_template('employee/dashboard.html',
                         my_tasks=my_tasks,
                         pending_tasks=pending_tasks,
                         in_progress_tasks=in_progress_tasks,
                         completed_tasks=completed_tasks)

@employee_bp.route('/profile')
@login_required
def profile():
    return render_template('employee/profile.html')