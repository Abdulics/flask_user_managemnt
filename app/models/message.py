from datetime import datetime
from app import db

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc), index=True, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)

    # relationships to User are declared by string to avoid circular imports
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        backref=db.backref("sent_messages", lazy="dynamic"),
    )
    recipient = db.relationship(
        "User",
        foreign_keys=[recipient_id],
        backref=db.backref("received_messages", lazy="dynamic"),
    )

    def mark_as_read(self):
        if not self.read:
            self.read = True
            db.session.add(self)
            db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "subject": self.subject,
            "body": self.body,
            "timestamp": None if self.timestamp is None else self.timestamp.isoformat(),
            "read": self.read,
        }

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.recipient_id}>"