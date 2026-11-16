
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Equipment

equipment_bp = Blueprint("equipment", __name__)

VALID_STATUSES = {
    "operational",
    "under_maintenance",
    "out_of_service"
}


def equipment_to_dict(equipment):
    return {
        "id": equipment.id,
        "name": equipment.name,
        "description": equipment.description,
        "serial_number": equipment.serial_number,
        "location": equipment.location,
        "status": equipment.status,
        "created_at": equipment.created_at.isoformat()
    }


@equipment_bp.route("", methods=["GET"])
def get_equipment():
    equipment = Equipment.query.order_by(Equipment.id).all()

    return jsonify([
        equipment_to_dict(item) for item in equipment
    ]), 200


@equipment_bp.route("/<int:equipment_id>", methods=["GET"])
def get_equipment_by_id(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)

    if equipment is None:
        return jsonify({"error": "Equipment not found"}), 404

    return jsonify(equipment_to_dict(equipment)), 200


@equipment_bp.route("", methods=["POST"])
def create_equipment():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A valid JSON object is required"}), 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Equipment name is required"}), 400

    for field in ("description", "serial_number", "location", "status"):
        if field in data and data[field] is not None:
            if not isinstance(data[field], str):
                return jsonify({"error": f"{field} must be a string"}), 400

    status = data.get("status", "operational")

    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid equipment status"}), 400

    equipment = Equipment(
        name=name.strip(),
        description=data.get("description"),
        serial_number=data.get("serial_number"),
        location=data.get("location"),
        status=status
    )

    try:
        db.session.add(equipment)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Serial number already exists"
        }), 409

    return jsonify(equipment_to_dict(equipment)), 201


@equipment_bp.route("/<int:equipment_id>", methods=["PUT"])
def update_equipment(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)

    if equipment is None:
        return jsonify({"error": "Equipment not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A valid JSON object is required"}), 400

    allowed_fields = {
        "name", "description", "serial_number", "location", "status"
    }

    if not data or set(data) - allowed_fields:
        return jsonify({"error": "Invalid or empty update fields"}), 400

    for field, value in data.items():
        if value is not None and not isinstance(value, str):
            return jsonify({"error": f"{field} must be a string"}), 400

    if "name" in data and (
        data["name"] is None or not data["name"].strip()
    ):
        return jsonify({"error": "Equipment name cannot be empty"}), 400

    if "status" in data and data["status"] not in VALID_STATUSES:
        return jsonify({"error": "Invalid equipment status"}), 400

    for field, value in data.items():
        setattr(
            equipment,
            field,
            value.strip() if isinstance(value, str) else value
        )

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Serial number already exists"
        }), 409

    return jsonify(equipment_to_dict(equipment)), 200


@equipment_bp.route("/<int:equipment_id>", methods=["DELETE"])
def delete_equipment(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)

    if equipment is None:
        return jsonify({"error": "Equipment not found"}), 404

    if equipment.maintenance_requests:
        return jsonify({
            "error": "Equipment with maintenance history cannot be deleted"
        }), 409

    db.session.delete(equipment)
    db.session.commit()

    return "", 204
