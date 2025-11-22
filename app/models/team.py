from datetime import datetime, timezone
from app import db

class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    department = db.relationship('Department', back_populates='teams')
    lead = db.relationship('Employee', foreign_keys=[lead_id])

    def __repr__(self):
        return f"<Team id={self.id} name={self.name!r}>"

