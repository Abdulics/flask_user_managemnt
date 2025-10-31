from datetime import datetime, timezone
from app import db
from app.models.user import team_members  # association table

class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class Team(db.Model, TimestampMixin):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    team_metadata = db.Column(db.JSON, nullable=False, default=dict)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", backref=db.backref("owned_teams", lazy="dynamic"), foreign_keys=[owner_id])

    # members relationship is provided automatically via User.teams backref

    def __repr__(self):
        return f"<Team id={self.id} name={self.name!r} slug={self.slug!r}>"

    def add_member(self, user):
        if not self.members.filter_by(id=user.id).first():
            self.members.append(user)

    def remove_member(self, user):
        if self.members.filter_by(id=user.id).first():
            self.members.remove(user)

    def member_ids(self):
        return [u.id for u in self.members.all()]

    def to_dict(self, include_members=False, include_owner=False):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "is_active": self.is_active,
            "team_metadata": self.team_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_owner and self.owner:
            data["owner"] = {"id": self.owner.id, "username": self.owner.username}
        if include_members:
            data["members"] = [{"id": m.id, "username": m.username} for m in self.members.all()]
        return data

    def from_dict(self, data):
        for field in ("name", "slug", "description"):
            if field in data:
                setattr(self, field, data[field])
        if "is_active" in data:
            self.is_active = bool(data["is_active"])
        if "team_metadata" in data:
            self.team_metadata = data["team_metadata"]
        if "owner_id" in data:
            self.owner_id = data["owner_id"]
