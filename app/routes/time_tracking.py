from datetime import datetime, timezone
from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app import db
from app.models.time_entry import TimeEntry

time_tracking_bp = Blueprint('time_tracking', __name__, url_prefix='/time-tracker')


def _get_active_entry(user_id: int):
    return TimeEntry.query.filter_by(user_id=user_id, clock_out=None).order_by(TimeEntry.clock_in.desc()).first()


@time_tracking_bp.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    existing = _get_active_entry(current_user.id)
    if existing:
        flash("Already clocked in.", "info")
        return redirect(url_for('main.dashboard'))
    entry = TimeEntry(user_id=current_user.id, clock_in=datetime.now(timezone.utc))
    db.session.add(entry)
    db.session.commit()
    flash("Clocked in.", "success")
    return redirect(url_for('main.dashboard'))


@time_tracking_bp.route('/clock-out', methods=['POST'])
@login_required
def clock_out():
    entry = _get_active_entry(current_user.id)
    if not entry:
        flash("No active session to clock out.", "warning")
        return redirect(url_for('main.dashboard'))
    entry.clock_out_now()
    db.session.commit()
    flash("Clocked out.", "success")
    return redirect(url_for('main.dashboard'))


@time_tracking_bp.route('/log')
@login_required
def log():
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.clock_in.desc()).limit(50).all()
    return render_template('time_tracking/log.html', entries=entries)
