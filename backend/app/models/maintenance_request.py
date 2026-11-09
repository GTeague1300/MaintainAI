from datetime import datetime, timezone

from app.extensions import db


class MaintenanceRequest(db.Model):
    __tablename__ = "maintenance_requests"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    priority = db.Column(db.String(20), default="medium", nullable=False)
    status = db.Column(db.String(30), default="open", nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship("User", backref="maintenance_requests")
    equipment = db.relationship("Equipment", backref="maintenance_requests")

    def __repr__(self):
        return f"<MaintenanceRequest {self.title}>"