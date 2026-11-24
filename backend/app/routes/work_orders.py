from flask import Blueprint, jsonify, request
from datetime import datetime, timezone

from app.extensions import db
from app.models import WorkOrder, MaintenanceRequest, User

work_orders_bp = Blueprint("work_orders", __name__)


def serialize_work_order(work_order):
    return {
        "id": work_order.id,
        "title": work_order.title,
        "description": work_order.description,
        "status": work_order.status,
        "maintenance_request_id": work_order.maintenance_request_id,
        "assigned_to": work_order.assigned_to,
        "assigned_engineer": (
            f"{work_order.assigned_engineer.first_name} "
            f"{work_order.assigned_engineer.last_name}"
            if work_order.assigned_engineer else None
        ),
        "created_at": work_order.created_at.isoformat(),
        "completed_at": (
            work_order.completed_at.isoformat()
            if work_order.completed_at else None
        )
    }

@work_orders_bp.route("/", methods=["GET"])
def get_work_orders():
    work_orders = WorkOrder.query.order_by(
        WorkOrder.created_at.desc()
    ).all()

    return jsonify([
        serialize_work_order(work_order)
        for work_order in work_orders
    ]), 200


@work_orders_bp.route("/<int:work_order_id>", methods=["GET"])
def get_work_order(work_order_id):
    work_order = db.session.get(WorkOrder, work_order_id)

    if not work_order:
        return jsonify({
            "error": "Work order not found"
        }), 404

    return jsonify(serialize_work_order(work_order)), 200

@work_orders_bp.route("/", methods=["POST"])
def create_work_order():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    title = data.get("title")
    description = data.get("description")
    maintenance_request_id = data.get("maintenance_request_id")
    assigned_to = data.get("assigned_to")

    # Validate required fields
    if not title or not isinstance(title, str):
        return jsonify({"error": "A valid title is required"}), 400

    if not description or not isinstance(description, str):
        return jsonify({"error": "A valid description is required"}), 400

    if not isinstance(maintenance_request_id, int) or isinstance(maintenance_request_id, bool):
        return jsonify({"error": "A valid maintenance request ID is required"}), 400

    # Check maintenance request exists
    maintenance_request = db.session.get(
        MaintenanceRequest,
        maintenance_request_id
    )

    if not maintenance_request:
        return jsonify({
            "error": "Maintenance request not found"
        }), 404

    # Validate assigned engineer if provided
    if assigned_to is not None:
        if not isinstance(assigned_to, int) or isinstance(assigned_to, bool):
            return jsonify({"error": "Invalid assigned engineer ID"}), 400

        engineer = db.session.get(User, assigned_to)

        if not engineer or engineer.role != "engineer" or not engineer.is_active:
            return jsonify({
                "error": "Assigned user must be an active engineer"
            }), 400

    # Create work order
    work_order = WorkOrder(
        title=title.strip(),
        description=description.strip(),
        maintenance_request_id=maintenance_request_id,
        assigned_to=assigned_to,
        status="assigned" if assigned_to else "open"
    )

    db.session.add(work_order)
    db.session.commit()

    return jsonify({
        "message": "Work order created successfully",
        "work_order": serialize_work_order(work_order)
    }), 201

@work_orders_bp.route("/<int:work_order_id>", methods=["PUT"])
def update_work_order(work_order_id):
    work_order = db.session.get(WorkOrder, work_order_id)

    if not work_order:
        return jsonify({
            "error": "Work order not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    # Validate and update title
    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "A valid title is required"}), 400

        work_order.title = data["title"].strip()

    # Validate and update description
    if "description" in data:
        if not isinstance(data["description"], str) or not data["description"].strip():
            return jsonify({"error": "A valid description is required"}), 400

        work_order.description = data["description"].strip()

    # Validate and update assigned engineer
    if "assigned_to" in data:
        assigned_to = data["assigned_to"]

        if assigned_to is not None:
            if not isinstance(assigned_to, int) or isinstance(assigned_to, bool):
                return jsonify({"error": "Invalid assigned engineer ID"}), 400

            engineer = db.session.get(User, assigned_to)

            if not engineer or engineer.role != "engineer" or not engineer.is_active:
                return jsonify({
                    "error": "Assigned user must be an active engineer"
                }), 400

        work_order.assigned_to = assigned_to

    # Validate and update maintenance request
    if "maintenance_request_id" in data:
        request_id = data["maintenance_request_id"]

        if not isinstance(request_id, int) or isinstance(request_id, bool):
            return jsonify({"error": "Invalid maintenance request ID"}), 400

        maintenance_request = db.session.get(MaintenanceRequest, request_id)

        if not maintenance_request:
            return jsonify({
                "error": "Maintenance request not found"
            }), 404

        work_order.maintenance_request_id = request_id

    # Validate and update status
    if "status" in data:
        allowed_statuses = [
            "open",
            "assigned",
            "in_progress",
            "completed",
            "cancelled"
        ]

        if data["status"] not in allowed_statuses:
            return jsonify({
                "error": "Invalid work order status"
            }), 400

        work_order.status = data["status"]

    # Update completion timestamp
    if work_order.status == "completed":
        if work_order.completed_at is None:
            work_order.completed_at = datetime.now(timezone.utc)
    else:
        work_order.completed_at = None

    db.session.commit()

    return jsonify({
        "message": "Work order updated successfully",
        "work_order": serialize_work_order(work_order)
    }), 200

@work_orders_bp.route("/<int:work_order_id>", methods=["DELETE"])
def delete_work_order(work_order_id):
    work_order = db.session.get(WorkOrder, work_order_id)

    if not work_order:
        return jsonify({
            "error": "Work order not found"
        }), 404

    db.session.delete(work_order)
    db.session.commit()

    return jsonify({
        "message": "Work order deleted successfully"
    }), 200