from app import db
from datetime import datetime, timezone

      
class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    employees = db.relationship('Employee', back_populates='department', lazy='dynamic')
    teams = db.relationship('Team', back_populates='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'