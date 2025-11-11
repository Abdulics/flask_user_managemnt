from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user    
from app.models.user import Role 
from app.models.employees import Employee
from app.models.task import Task
from app.utils.decorators import role_required
from app import db

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')


@manager_bp.route('/dashboard')
@login_required
@role_required(Role.MANAGER)
@role_required(Role.ADMIN)
def manager_dashboard():
    if not current_user.employee:
        flash('Manager account not linked to employee record.', 'danger')
        return redirect(url_for('dashboard'))
    
    subordinates = Employee.query.filter_by(manager_id=current_user.employee.id).all()
    
    subordinate_user_ids = [sub.user.id for sub in subordinates if sub.user]
    pending_tasks = Task.query.filter(
        Task.assigned_to_id.in_(subordinate_user_ids),
        Task.status.in_(['pending', 'in_progress'])
    ).count() if subordinate_user_ids else 0
    
    return render_template('manager/dashboard.html',
                         subordinates=subordinates,
                         pending_tasks=pending_tasks)

@manager_bp.route('/team')
@login_required
@role_required(Role.MANAGER)
@role_required(Role.ADMIN)
def view_team():
    if not current_user.employee:
        flash('Manager account not linked to employee record.', 'danger')
        return redirect(url_for('dashboard'))
    
    subordinates = Employee.query.filter_by(manager_id=current_user.employee.id).all()
    return render_template('manager/team.html', subordinates=subordinates)


@manager_bp.route('/team/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(Role.MANAGER)
@role_required(Role.ADMIN)
def edit_subordinate(id):
    employee = Employee.query.get_or_404(id)
    
    if not current_user.employee or employee.manager_id != current_user.employee.id:
        flash('You can only edit employees you manage.', 'danger')
        return redirect(url_for('manager.view_team'))
    
    if not employee.user:
        flash('This employee does not have a user account yet.', 'warning')
        return redirect(url_for('manager.view_team'))
    
    if request.method == 'POST':
        employee.user.username = request.form.get('username')
        
        new_password = request.form.get('new_password')
        if new_password:
            employee.user.set_password(new_password)
        
        try:
            db.session.commit()
            flash(f'User account for {employee.full_name} updated successfully!', 'success')
            return redirect(url_for('manager.view_team'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('manager/edit_subordinate.html', employee=employee)
