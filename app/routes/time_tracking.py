from datetime import datetime, timedelta, timezone
from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.time_entry import TimeEntry

time_tracking_bp = Blueprint('time_tracking', __name__, url_prefix='/time-tracker')


def _get_active_entry(user_id: int):
    return TimeEntry.query.filter_by(user_id=user_id, clock_out=None).order_by(TimeEntry.clock_in.desc()).first()


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.astimezone(timezone.utc)
    return value.astimezone(timezone.utc)


def _duration_seconds(entry, now):
    clock_in = _as_utc(entry.clock_in)
    clock_out = _as_utc(entry.clock_out) or now
    if not clock_in:
        return 0
    return max(0, int((clock_out - clock_in).total_seconds()))


def _hours(seconds):
    return round(seconds / 3600, 2)


@time_tracking_bp.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    existing = _get_active_entry(current_user.id)
    if existing:
        flash("Already clocked in.", "info")
        return redirect(url_for('main.dashboard'))
    entry = TimeEntry(user_id=current_user.id, clock_in=datetime.now(timezone.utc))
    db.session.add(entry)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Already clocked in.", "info")
        return redirect(url_for('main.dashboard'))
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
    now = datetime.now(timezone.utc)
    today = now.date()
    week_start = now - timedelta(days=7)
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.clock_in.desc()).limit(100).all()

    today_seconds = 0
    week_seconds = 0
    completed_count = 0

    for entry in entries:
        clock_in = _as_utc(entry.clock_in)
        if not clock_in:
            continue

        duration = _duration_seconds(entry, now)
        if entry.clock_out:
            completed_count += 1
        if clock_in.date() == today:
            today_seconds += duration
        if clock_in >= week_start:
            week_seconds += duration

    return render_template(
        'time_tracking/log.html',
        entries=entries,
        now=now,
        today_hours=_hours(today_seconds),
        week_hours=_hours(week_seconds),
        completed_count=completed_count,
    )
