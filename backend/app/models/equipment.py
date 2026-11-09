from datetime import datetime, timezone

from app.extensions import db


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    serial_number = db.Column(db.String(100), unique=True)
    location = db.Column(db.String(150))
    status = db.Column(db.String(30), default="operational", nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Equipment {self.name}>"