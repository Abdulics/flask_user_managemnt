from datetime import datetime, timezone
from app import db


class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    clock_in = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    clock_out = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref=db.backref("time_entries", lazy="dynamic"))

    @property
    def is_active(self) -> bool:
        return self.clock_out is None

    def clock_out_now(self):
        self.clock_out = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<TimeEntry id={self.id} user_id={self.user_id} active={self.is_active}>"
