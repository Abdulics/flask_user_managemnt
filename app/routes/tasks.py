from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.task import Task
from app.models.user import User
from app.models.employees import Employee, Role
from datetime import datetime, timezone

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
        assigned_to_id = int(request.form.get('assigned_to_id'))
        if current_user.is_manager and not current_user.is_admin:
            assigned_user = db.get_or_404(User, assigned_to_id)
            if not assigned_user.employee or assigned_user.employee.manager_id != current_user.employee.id:
                flash('Managers can only assign tasks to their own team members.', 'danger')
                return redirect(url_for('tasks.create_task'))

        task = Task(
            title=request.form.get('title'),
            description=request.form.get('description'),
            status='pending',
            priority=request.form.get('priority'),
            assigned_to_id=assigned_to_id,
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
    
    if current_user.is_admin:
        users = User.query.filter_by(is_active=True).all()
    else:
        subordinate_ids = [
            emp.user.id
            for emp in Employee.query.filter_by(manager_id=current_user.employee.id).all()
            if emp.user and emp.user.is_active
        ]
        users = User.query.filter(User.id.in_(subordinate_ids)).order_by(User.username).all() if subordinate_ids else []
    return render_template('tasks/create.html', users=users)


@task_bp.route('/<int:id>')
@login_required
def view_task(id):
    task = db.get_or_404(Task, id)
    
    if task.assigned_to_id != current_user.id and task.created_by_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('tasks.my_tasks'))
    
    return render_template('tasks/view.html', task=task)


@task_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    task = db.get_or_404(Task, id)
    
    if task.assigned_to_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('tasks.my_tasks'))
    
    new_status = request.form.get('status')
    task.status = new_status
    
    if new_status == 'completed':
        task.completed_at = datetime.now(timezone.utc)
    
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
