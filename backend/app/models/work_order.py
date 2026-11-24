from datetime import datetime, timezone

from app.extensions import db


class WorkOrder(db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(30),
        default="open",
        nullable=False
    )

    maintenance_request_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_requests.id"),
        nullable=False
    )

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    completed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    maintenance_request = db.relationship(
        "MaintenanceRequest",
        backref="work_orders"
    )

    assigned_engineer = db.relationship(
        "User",
        foreign_keys=[assigned_to]
    )

    def __repr__(self):
        return f"<WorkOrder {self.title}>"