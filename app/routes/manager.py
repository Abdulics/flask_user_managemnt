from flask import Blueprint, render_template
from flask_login import login_required, current_user    
from app.models.user import Role
from app.models.user import User    
from app.models.employees import Employee
from app.models.task import Task
from app.utils.decorators import role_required
from app import db

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')


@manager_bp.route('/dashboard')
@login_required
@role_required(Role.MANAGER)
def manager_dashboard():
    # Fetch team members
    team_members = db.session.execute(
        db.select(User).join(Employee).filter(Employee.manager_id == current_user.employee.id)
    ).scalars().all()

    # Fetch recent tasks assigned to team members
    recent_tasks = db.session.execute(
        db.select(Task).join(Employee).filter(Employee.manager_id == current_user.employee.id).order_by(Task.created_at.desc()).limit(5)
    ).scalars().all()

    return render_template('dashboard/manager_dashboard.html', team_members=team_members, recent_tasks=recent_tasks)

@manager_bp.route('/team')
@login_required
@role_required(Role.MANAGER)
def view_team():
    team_members = db.session.execute(
        db.select(User).join(Employee).filter(Employee.manager_id == current_user.employee.id)
    ).scalars().all()
    return render_template('manager/view_team.html', team_members=team_members)

@manager_bp.route('/tasks')
@login_required 
@role_required(Role.MANAGER)
def view_tasks():
    tasks = db.session.execute(
        db.select(Task).join(Employee).filter(Employee.manager_id == current_user.employee.id)
    ).scalars().all()
    return render_template('manager/view_tasks.html', tasks=tasks)

@manager_bp.route('/task/<int:task_id>')
@login_required
@role_required(Role.MANAGER)
def view_task_detail(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.employee.manager_id != current_user.employee.id:
        return "Task not found or access denied", 404
    return render_template('manager/view_task_detail.html', task=task)

@manager_bp.route('/team/member/<int:member_id>')
@login_required
@role_required(Role.MANAGER)
def view_team_member(member_id):
    member = db.session.get(User, member_id)
    if not member or member.employee.manager_id != current_user.employee.id:
        return "Team member not found or access denied", 404
    return render_template('manager/view_team_member.html', member=member)

@manager_bp.route('/add_team_member', methods=['GET', 'POST'])
@login_required
@role_required(Role.MANAGER)
def add_team_member():
    # Implementation for adding a new team member
    return "Add Team Member Page - To be implemented"


@manager_bp.route('/manage_tasks', methods=['GET', 'POST'])
@login_required
@role_required(Role.MANAGER)
def manage_tasks():
    # Implementation for managing tasks
    return "Manage Tasks Page - To be implemented"

