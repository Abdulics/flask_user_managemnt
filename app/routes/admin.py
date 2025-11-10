from datetime import datetime, timezone
from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms.dashboard_forms import DashboardActionForm
from flask_login import login_required, current_user
from app import db

from app.models.user import Role, User
from app.utils.decorators import role_required

admin_admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_admin_bp.route('/manage-users')
@login_required
@role_required(Role.ADMIN)
def manage_users():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars().all()
    return render_template('admin/manage_users.html', users=users)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
@role_required(Role.ADMIN)
def admin_dashboard():
    total_employees = Employee.query.count()
    total_users = User.query.count()
    total_departments = Department.query.count()
    total_teams = Team.query.count()
    
    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_employees=total_employees,
                         total_users=total_users,
                         total_departments=total_departments,
                         total_teams=total_teams,
                         recent_employees=recent_employees)


@admin_bp.route('/employees')
@login_required
@admin_required
def list_employees():
    employees = Employee.query.all()
    return render_template('admin/employees.html', employees=employees)


@admin_bp.route('/employees/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_employee():
    if request.method == 'POST':
        employee = Employee(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            position=request.form.get('position'),
            hire_date=datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d').date() if request.form.get('hire_date') else None,
            salary=float(request.form.get('salary')) if request.form.get('salary') else None,
            address=request.form.get('address'),
            emergency_contact=request.form.get('emergency_contact'),
            emergency_phone=request.form.get('emergency_phone'),
            department_id=int(request.form.get('department_id')) if request.form.get('department_id') else None,
            manager_id=int(request.form.get('manager_id')) if request.form.get('manager_id') else None
        )
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash(f'Employee {employee.full_name} created successfully!', 'success')
            return redirect(url_for('admin.list_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating employee: {str(e)}', 'danger')
    
    departments = Department.query.all()
    managers = Employee.query.all()
    return render_template('admin/create_employee.html', departments=departments, managers=managers)


@admin_bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        employee.email = request.form.get('email')
        employee.phone = request.form.get('phone')
        employee.position = request.form.get('position')
        employee.hire_date = datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d').date() if request.form.get('hire_date') else None
        employee.salary = float(request.form.get('salary')) if request.form.get('salary') else None
        employee.address = request.form.get('address')
        employee.emergency_contact = request.form.get('emergency_contact')
        employee.emergency_phone = request.form.get('emergency_phone')
        employee.department_id = int(request.form.get('department_id')) if request.form.get('department_id') else None
        employee.manager_id = int(request.form.get('manager_id')) if request.form.get('manager_id') else None
        
        try:
            db.session.commit()
            flash(f'Employee {employee.full_name} updated successfully!', 'success')
            return redirect(url_for('admin.list_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'danger')
    
    departments = Department.query.all()
    managers = Employee.query.filter(Employee.id != id).all()
    return render_template('admin/edit_employee.html', employee=employee, departments=departments, managers=managers)


@admin_bp.route('/employees/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    try:
        if employee.user:
            db.session.delete(employee.user)
        db.session.delete(employee)
        db.session.commit()
        flash(f'Employee {employee.full_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
    
    return redirect(url_for('admin.list_employees'))


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.is_active = request.form.get('is_active') == 'on'
        
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/departments')
@login_required
@admin_required
def list_departments():
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)


@admin_bp.route('/departments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_department():
    if request.method == 'POST':
        department = Department(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        
        try:
            db.session.add(department)
            db.session.commit()
            flash(f'Department {department.name} created successfully!', 'success')
            return redirect(url_for('admin.list_departments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating department: {str(e)}', 'danger')
    
    return render_template('admin/create_department.html')


@admin_bp.route('/teams')
@login_required
@admin_required
def list_teams():
    teams = Team.query.all()
    return render_template('admin/teams.html', teams=teams)


@admin_bp.route('/teams/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_team():
    if request.method == 'POST':
        team = Team(
            name=request.form.get('name'),
            description=request.form.get('description'),
            department_id=int(request.form.get('department_id')) if request.form.get('department_id') else None,
            lead_id=int(request.form.get('lead_id')) if request.form.get('lead_id') else None
        )
        
        try:
            db.session.add(team)
            db.session.commit()
            flash(f'Team {team.name} created successfully!', 'success')
            return redirect(url_for('admin.list_teams'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating team: {str(e)}', 'danger')
    
    departments = Department.query.all()
    employees = Employee.query.all()
    return render_template('admin/create_team.html', departments=departments, employees=employees)
