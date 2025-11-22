from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.attendance import Attendance
from app.models.employees import Employee, Role
from app.utils.decorators import role_required
from app.forms.attendance_forms import AttendanceForm

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


def _get_subordinate_user_ids(manager_employee_id: int) -> list[int]:
    """Return user IDs for employees managed by the given manager employee."""
    return [
        emp.user.id for emp in Employee.query.filter_by(manager_id=manager_employee_id).all() if emp.user
    ]


@attendance_bp.route('/', methods=['GET', 'POST'])
@login_required
def view_or_mark_attendance():
    """Employees can view and mark their own attendance for today."""
    target_user = current_user
    form = AttendanceForm()

    if form.validate_on_submit():
        record = Attendance.for_user_on_date(user_id=target_user.id, target_date=date.today(), create_if_missing=True)
        record.status = form.status.data
        record.note = form.note.data
        db.session.add(record)
        db.session.commit()
        flash('Attendance updated.', 'success')
        return redirect(url_for('attendance.view_or_mark_attendance'))

    records = Attendance.query.filter_by(user_id=target_user.id).order_by(Attendance.date.desc()).limit(30).all()
    return render_template('attendance/index.html', records=records, target_user=target_user, form=form)


@attendance_bp.route('/team')
@login_required
@role_required(Role.ADMIN, Role.MANAGER)
def team_attendance():
    """Managers/Admins can review team attendance."""
    if current_user.is_admin:
        records = Attendance.query.order_by(Attendance.date.desc()).limit(200).all()
    else:
        subordinate_ids = _get_subordinate_user_ids(current_user.employee.id)
        records = Attendance.query.filter(Attendance.user_id.in_(subordinate_ids)).order_by(Attendance.date.desc()).all()

    return render_template('attendance/team.html', records=records)
