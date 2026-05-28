from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.timeoff import TimeOff, TimeOffStatus, TimeOffType
from app.models.employees import Employee, Role
from app.models.department import Department
from app.utils.decorators import role_required
from app.forms.timeoff_forms import TimeOffRequestForm
from app.models.message import Message

timeoff_bp = Blueprint('timeoff', __name__, url_prefix='/timeoff')


def _get_subordinate_user_ids(manager_employee_id: int) -> list[int]:
    return [
        emp.user.id for emp in Employee.query.filter_by(manager_id=manager_employee_id).all() if emp.user
    ]

def _is_hr(user) -> bool:
    if not user.employee:
        return False
    dept = user.employee.department.name.lower() if user.employee.department else ""
    return dept == "human resources"


def _can_review_team_timeoff(user) -> bool:
    return user.is_admin or user.is_manager


def _can_review_hr_timeoff(user) -> bool:
    return user.is_admin or _is_hr(user)


def _hr_user_ids() -> list[int]:
    return [
        emp.user.id
        for emp in Employee.query.join(Employee.department).filter(db.func.lower(Department.name) == "human resources").all()
        if emp.user
    ]

def _notify(user_from, user_to_id: int, subject: str, body: str):
    if not user_to_id:
        return
    msg = Message(
        subject=subject,
        body=body,
        sender_id=user_from.id,
        recipient_id=user_to_id
    )
    db.session.add(msg)


@timeoff_bp.route('/', methods=['GET', 'POST'])
@login_required
def my_timeoff():
    """Employees submit and view their own time off requests."""
    form = TimeOffRequestForm()
    if form.validate_on_submit():
        timeoff = TimeOff(
            user_id=current_user.id,
            type=TimeOffType(form.type.data),
            status=TimeOffStatus.PENDING,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data or None
        )
        # default manager is the user's manager
        if current_user.employee and current_user.employee.manager:
            timeoff.manager_id = current_user.employee.manager.user.id if current_user.employee.manager.user else None
        db.session.add(timeoff)
        if timeoff.manager_id:
            _notify(
                current_user,
                timeoff.manager_id,
                "Time off request submitted",
                f"{current_user.username} submitted a time-off request for {timeoff.start_date} to {timeoff.end_date}.",
            )
        db.session.commit()
        flash('Time-off request submitted.', 'success')
        return redirect(url_for('timeoff.my_timeoff'))

    requests = TimeOff.query.filter_by(user_id=current_user.id).order_by(TimeOff.created_at.desc()).all()
    return render_template('timeoff/index.html', requests=requests, form=form)


@timeoff_bp.route('/team')
@login_required
def review_team_requests():
    """Managers review subordinate requests; HR/admin can also view."""
    if not _can_review_team_timeoff(current_user):
        flash("Access denied. Team time-off review is for managers and admins.", "danger")
        return redirect(url_for('main.dashboard'))
    if current_user.is_admin:
        requests = TimeOff.query.order_by(TimeOff.created_at.desc()).all()
    else:
        subordinate_ids = _get_subordinate_user_ids(current_user.employee.id)
        requests = TimeOff.query.filter(TimeOff.user_id.in_(subordinate_ids), TimeOff.status == TimeOffStatus.PENDING).order_by(TimeOff.created_at.desc()).all()
    return render_template('timeoff/review.html', requests=requests, is_hr=False)


@timeoff_bp.route('/hr')
@login_required
def hr_queue():
    """HR review queue for manager-approved requests."""
    if not _can_review_hr_timeoff(current_user):
        flash("Access denied. HR only.", "danger")
        return redirect(url_for('main.dashboard'))
    requests = TimeOff.query.filter_by(status=TimeOffStatus.MANAGER_APPROVED).order_by(TimeOff.created_at.desc()).all()
    return render_template('timeoff/review.html', requests=requests, is_hr=True)


@timeoff_bp.route('/<int:request_id>/<action>', methods=['POST'])
@login_required
def act_on_request(request_id, action):
    timeoff = db.get_or_404(TimeOff, request_id)
    stage = request.form.get("stage")

    is_hr_stage = stage == "hr"

    if is_hr_stage and not _can_review_hr_timeoff(current_user):
        flash("Access denied. HR only.", "danger")
        return redirect(url_for('main.dashboard'))

    if not is_hr_stage and not _can_review_team_timeoff(current_user):
        flash("Access denied. Team time-off review is for managers and admins.", "danger")
        return redirect(url_for('main.dashboard'))

    # Managers can only act on their direct subordinates.
    if not is_hr_stage and current_user.is_manager and not current_user.is_admin:
        if not timeoff.user.employee or timeoff.user.employee.manager_id != current_user.employee.id:
            flash('You cannot act on requests outside your team.', 'danger')
            return redirect(url_for('timeoff.review_team_requests'))

    # Manager step -> move to HR queue
    if not is_hr_stage:
        if timeoff.status != TimeOffStatus.PENDING:
            flash('Only pending requests can be reviewed by a manager.', 'warning')
            return redirect(url_for('timeoff.review_team_requests'))
        if action == 'approve':
            timeoff.status = TimeOffStatus.MANAGER_APPROVED
            timeoff.manager_id = current_user.id
            timeoff.manager_decision_at = datetime.now(timezone.utc)
            _notify(current_user, timeoff.user_id, "Time off sent to HR", "Your manager approved your time-off request and sent it to HR.")
            for hr_user_id in _hr_user_ids():
                if hr_user_id != current_user.id:
                    _notify(current_user, hr_user_id, "Time off awaiting HR review", f"{timeoff.user.username}'s time-off request is waiting in the HR queue.")
            flash('Request sent to HR for approval.', 'success')
        elif action == 'deny':
            timeoff.status = TimeOffStatus.DENIED
            timeoff.manager_id = current_user.id
            timeoff.manager_decision_at = datetime.now(timezone.utc)
            _notify(current_user, timeoff.user_id, "Time off denied", "Your manager denied your time-off request.")
            flash('Request denied.', 'success')
        else:
            flash('Invalid action.', 'danger')
        db.session.commit()
        return redirect(url_for('timeoff.review_team_requests'))

    # HR/admin step on manager-approved requests
    if is_hr_stage:
        if timeoff.status != TimeOffStatus.MANAGER_APPROVED:
            flash('Only manager-approved requests can be reviewed by HR.', 'warning')
            return redirect(url_for('timeoff.hr_queue'))
        if action == 'approve':
            timeoff.approve()
            timeoff.hr_id = current_user.id
            timeoff.hr_decision_at = datetime.now(timezone.utc)
            _notify(current_user, timeoff.user_id, "Time off approved", "Your time-off request was approved by HR.")
            if timeoff.manager_id:
                _notify(current_user, timeoff.manager_id, "Time off approved (team)", f"{timeoff.user.username}'s request was approved by HR.")
            flash('Request approved.', 'success')
        elif action == 'deny':
            timeoff.deny()
            timeoff.hr_id = current_user.id
            timeoff.hr_decision_at = datetime.now(timezone.utc)
            _notify(current_user, timeoff.user_id, "Time off denied", "Your time-off request was denied by HR.")
            if timeoff.manager_id:
                _notify(current_user, timeoff.manager_id, "Time off denied (team)", f"{timeoff.user.username}'s request was denied by HR.")
            flash('Request denied.', 'success')
        else:
            flash('Invalid action.', 'danger')
        db.session.commit()
        return redirect(url_for('timeoff.hr_queue'))

    flash('Invalid action.', 'danger')
    return redirect(url_for('timeoff.review_team_requests'))


@timeoff_bp.route('/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    timeoff = db.get_or_404(TimeOff, request_id)
    if timeoff.user_id != current_user.id:
        flash('You can only cancel your own time-off requests.', 'danger')
        return redirect(url_for('timeoff.my_timeoff'))
    if timeoff.status != TimeOffStatus.PENDING:
        flash('Only pending time-off requests can be cancelled.', 'warning')
        return redirect(url_for('timeoff.my_timeoff'))

    timeoff.cancel()
    db.session.commit()
    flash('Time-off request cancelled.', 'success')
    return redirect(url_for('timeoff.my_timeoff'))
