from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.task import Task
from app.models.user import User
from app.models.employees import Role
from datetime import datetime

from app.utils.decorators import role_required

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@task_bp.route('/')
@login_required
def my_tasks():
    status_filter = request.args.get('status', 'all')
    
    query = Task.query.filter_by(assigned_to_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    tasks = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()
    
    return render_template('tasks/my_tasks.html', tasks=tasks, status_filter=status_filter)


@task_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.MANAGER)
def create_task():
    if request.method == 'POST':
        task = Task(
            title=request.form.get('title'),
            description=request.form.get('description'),
            status='pending',
            priority=request.form.get('priority'),
            assigned_to_id=int(request.form.get('assigned_to_id')),
            created_by_id=current_user.id,
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None
        )
        
        try:
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.my_tasks'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating task: {str(e)}', 'danger')
    
    users = User.query.filter_by(is_active=True).all()
    return render_template('tasks/create.html', users=users)


@task_bp.route('/<int:id>')
@login_required
def view_task(id):
    task = Task.query.get_or_404(id)
    
    if task.assigned_to_id != current_user.id and task.created_by_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('tasks.my_tasks'))
    
    return render_template('tasks/view.html', task=task)


@task_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    task = Task.query.get_or_404(id)
    
    if task.assigned_to_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('tasks.my_tasks'))
    
    new_status = request.form.get('status')
    task.status = new_status
    
    if new_status == 'completed':
        task.completed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'danger')
    
    return redirect(url_for('tasks.view_task', id=id))


@task_bp.route('/assigned')
@login_required
@role_required(Role.ADMIN, Role.MANAGER)
def assigned_tasks():
    tasks = Task.query.filter_by(created_by_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks/assigned.html', tasks=tasks)
