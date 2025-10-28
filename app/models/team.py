from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app import db
from app.models.user import team_members  # association table declared in user.py

class TimestampMixin:
        """Reusable timestamp fields (kept local to avoid circular imports)."""
        created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
        updated_at = db.Column(
            db.DateTime,
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

class Team(db.Model, TimestampMixin):
        """
        Team model that complements the User model.

        Attributes:
        - id: PK
        - name: human-readable unique name
        - slug: URL-safe unique identifier
        - description: optional freeform text
        - is_active: boolean flag for soft-deactivation
        - metadata: JSON blob for arbitrary team data
        - owner_id: optional FK to user.id (team owner/creator)
        - owner: relationship to the owning User (string-based to avoid import cycles)
        - members: populated via the team_members association table (backref configured in user.py)
        """
        __tablename__ = "team"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), unique=True, nullable=False, index=True)
        slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
        description = db.Column(db.Text, nullable=True)

        is_active = db.Column(db.Boolean, nullable=False, default=True)
        metadata = db.Column(db.JSON, nullable=False, default=dict)

        owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
        owner = db.relationship("User", backref=db.backref("owned_teams", lazy="dynamic"), foreign_keys=[owner_id])

        # Note: the many-to-many relationship is declared on the User model with a backref "members".
        # This means Team will expose `members` automatically (the backref was created with lazy="dynamic").
        # If you prefer an explicit relationship here, you can also do:
        # members = db.relationship("User", secondary=team_members, backref=db.backref("teams", lazy="dynamic"), lazy="dynamic")

        def __repr__(self) -> str:
            return f"<Team id={self.id} name={self.name!r} slug={self.slug!r}>"

        def add_member(self, user) -> None:
            """Add a user to the team if not already a member."""
            # members is a dynamic relationship (Query) via backref; use query to check membership.
            if not self.members.filter_by(id=user.id).first():
                # appending to the relationship will create the association row
                self.members.append(user)

        def remove_member(self, user) -> None:
            """Remove a user from the team (no-op if not a member)."""
            if self.members.filter_by(id=user.id).first():
                self.members.remove(user)

        def member_ids(self) -> List[int]:
            """Return a list of member IDs (materializes the query)."""
            return [u.id for u in self.members.all()]

        def to_dict(self, include_members: bool = False, include_owner: bool = False) -> Dict[str, Any]:
            data: Dict[str, Any] = {
                "id": self.id,
                "name": self.name,
                "slug": self.slug,
                "description": self.description,
                "is_active": self.is_active,
                "metadata": self.metadata,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }
            if include_owner and self.owner is not None:
                # include minimal owner info to avoid loading full object deeply
                data["owner"] = {"id": self.owner.id, "username": self.owner.username}
            if include_members:
                # return minimal member info
                data["members"] = [{"id": m.id, "username": m.username} for m in self.members.all()]
            return data

        def from_dict(self, data: Dict[str, Any]) -> None:
            """
            Update writable fields from a dict.
            Does not manage members; use add_member/remove_member for that.
            """
            for field in ("name", "slug", "description"):
                if field in data:
                    setattr(self, field, data[field])
            if "is_active" in data:
                self.is_active = bool(data["is_active"])
            if "metadata" in data:
                self.metadata = data["metadata"]
            if "owner_id" in data:
                self.owner_id = data["owner_id"]


    
    