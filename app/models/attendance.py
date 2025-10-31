from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from app import db

class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
class AttendanceStatus(PyEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(db.Model, TimestampMixin):
    """
    Attendance record for a user on a particular date.

    - user_id: FK to users.id
    - date: the day the attendance applies to (one record per user/date)
    - status: one of AttendanceStatus
    - note: optional free text (reason, comment, etc.)
    - created_at / updated_at: timestamps
    """
    __tablename__ = "attendances"
    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uix_user_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum(AttendanceStatus, name="attendance_status"), nullable=False, default=AttendanceStatus.PRESENT)
    note = db.Column(db.Text, nullable=True)

    # relationship: expects User model to define back_populates="attendances" or similar
    user = db.relationship("User", back_populates="attendances", lazy="joined")

    def __repr__(self):
        return f"<Attendance id={self.id} user_id={self.user_id} date={self.date} status={self.status.value}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "status": self.status.value if self.status else None,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def mark(self, status: AttendanceStatus, note: str | None = None):
        """
        Mark attendance for this record. Call session.commit() externally.
        """
        if not isinstance(status, AttendanceStatus):
            raise ValueError("status must be an AttendanceStatus enum value")
        self.status = status
        if note is not None:
            self.note = note
        self.updated_at = datetime.utcnow()

    @classmethod
    def for_user_on_date(cls, user_id: int, target_date: date, create_if_missing: bool = False): # type: ignore
        """
        Helper to get attendance record for a given user and date.
        If create_if_missing is True, returns a new unsaved instance when none exists.
        """
        record = cls.query.filter_by(user_id=user_id, date=target_date).one_or_none()
        if record is None and create_if_missing:
            record = cls(user_id=user_id, date=target_date)
        return record