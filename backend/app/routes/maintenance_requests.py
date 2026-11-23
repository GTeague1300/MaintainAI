
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import MaintenanceRequest, User, Equipment


maintenance_requests_bp = Blueprint(
    "maintenance_requests",
    __name__
)


# Convert a maintenance request into a dictionary for JSON responses
def maintenance_request_to_dict(maintenance_request):
    return {
        "id": maintenance_request.id,
        "title": maintenance_request.title,
        "description": maintenance_request.description,
        "priority": maintenance_request.priority,
        "status": maintenance_request.status,
        "user_id": maintenance_request.user_id,
        "equipment_id": maintenance_request.equipment_id,
        "equipment_name": maintenance_request.equipment.name,
        "created_at": maintenance_request.created_at.isoformat()
    }


# GET all maintenance requests
@maintenance_requests_bp.route("", methods=["GET"])
def get_maintenance_requests():
    requests = MaintenanceRequest.query.order_by(
        MaintenanceRequest.id
    ).all()

    return jsonify([
        maintenance_request_to_dict(item) for item in requests
    ]), 200


# GET one maintenance request
@maintenance_requests_bp.route("/<int:request_id>", methods=["GET"])
def get_maintenance_request(request_id):
    maintenance_request = db.session.get(
        MaintenanceRequest, request_id
    )

    if maintenance_request is None:
        return jsonify({"error": "Maintenance request not found"}), 404

    return jsonify(
        maintenance_request_to_dict(maintenance_request)
    ), 200


# CREATE a maintenance request
@maintenance_requests_bp.route("", methods=["POST"])
def create_maintenance_request():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "medium")
    user_id = data.get("user_id")
    equipment_id = data.get("equipment_id")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A title is required"}), 400

    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "A description is required"}), 400

    if priority not in ["low", "medium", "high", "urgent"]:
        return jsonify({"error": "Invalid priority"}), 400

    if not isinstance(user_id, int) or isinstance(user_id, bool):
        return jsonify({"error": "A valid user_id is required"}), 400

    if not isinstance(equipment_id, int) or isinstance(equipment_id, bool):
        return jsonify({"error": "A valid equipment_id is required"}), 400

    user = db.session.get(User, user_id)
    equipment = db.session.get(Equipment, equipment_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if equipment is None:
        return jsonify({"error": "Equipment not found"}), 404

    maintenance_request = MaintenanceRequest(
        title=title.strip(),
        description=description.strip(),
        priority=priority,
        user_id=user_id,
        equipment_id=equipment_id
    )

    try:
        db.session.add(maintenance_request)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Could not create maintenance request"}), 400

    return jsonify(
        maintenance_request_to_dict(maintenance_request)
    ), 201


# UPDATE a maintenance request
@maintenance_requests_bp.route("/<int:request_id>", methods=["PUT"])
def update_maintenance_request(request_id):
    maintenance_request = db.session.get(
        MaintenanceRequest, request_id
    )

    if maintenance_request is None:
        return jsonify({"error": "Maintenance request not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    allowed_fields = ["title", "description", "priority", "status"]

    if not data or any(key not in allowed_fields for key in data):
        return jsonify({"error": "Invalid or empty update fields"}), 400

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        maintenance_request.title = data["title"].strip()

    if "description" in data:
        if not isinstance(data["description"], str) or not data["description"].strip():
            return jsonify({"error": "Description cannot be empty"}), 400
        maintenance_request.description = data["description"].strip()

    if "priority" in data:
        if data["priority"] not in ["low", "medium", "high", "urgent"]:
            return jsonify({"error": "Invalid priority"}), 400
        maintenance_request.priority = data["priority"]

    if "status" in data:
        if data["status"] not in ["open", "in_progress", "resolved"]:
            return jsonify({"error": "Invalid status"}), 400
        maintenance_request.status = data["status"]

    db.session.commit()

    return jsonify(
        maintenance_request_to_dict(maintenance_request)
    ), 200


# DELETE a maintenance request
@maintenance_requests_bp.route("/<int:request_id>", methods=["DELETE"])
def delete_maintenance_request(request_id):
    maintenance_request = db.session.get(
        MaintenanceRequest, request_id
    )

    if maintenance_request is None:
        return jsonify({"error": "Maintenance request not found"}), 404

    db.session.delete(maintenance_request)
    db.session.commit()

    return "", 204
