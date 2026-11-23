
import pytest

from app.extensions import db
from app.models import Equipment, User, MaintenanceRequest


@pytest.fixture
def setup_records(app):
    with app.app_context():
        user = User(
            email="maintenance-test@example.com",
            password_hash="test-password-hash",
            first_name="Test",
            last_name="User"
        )

        equipment = Equipment(
            name="Test Pump",
            serial_number="MAINTENANCE-TEST-001"
        )

        db.session.add_all([user, equipment])
        db.session.commit()

        return user.id, equipment.id


def test_get_all_maintenance_requests(client, setup_records):
    user_id, equipment_id = setup_records

    client.post("/api/maintenance-requests", json={
        "title": "Pump inspection",
        "description": "Pump needs inspecting",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    response = client.get("/api/maintenance-requests")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "Pump inspection"


def test_get_maintenance_request_by_id(client, setup_records):
    user_id, equipment_id = setup_records

    create_response = client.post("/api/maintenance-requests", json={
        "title": "Motor fault",
        "description": "Motor making unusual noises",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    request_id = create_response.json["id"]

    response = client.get(
        f"/api/maintenance-requests/{request_id}"
    )

    assert response.status_code == 200
    assert response.json["title"] == "Motor fault"
    assert response.json["equipment_name"] == "Test Pump"


def test_get_nonexistent_maintenance_request(client):
    response = client.get("/api/maintenance-requests/999")

    assert response.status_code == 404
    assert response.json["error"] == "Maintenance request not found"


def test_create_maintenance_request(client, setup_records):
    user_id, equipment_id = setup_records

    response = client.post("/api/maintenance-requests", json={
        "title": "Broken pump",
        "description": "Pump has stopped working",
        "priority": "high",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    assert response.status_code == 201
    assert response.json["title"] == "Broken pump"
    assert response.json["priority"] == "high"
    assert response.json["status"] == "open"


def test_create_maintenance_request_without_title(
    client, setup_records
):
    user_id, equipment_id = setup_records

    response = client.post("/api/maintenance-requests", json={
        "description": "Pump has stopped working",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    assert response.status_code == 400
    assert response.json["error"] == "A title is required"


def test_create_maintenance_request_with_invalid_priority(
    client, setup_records
):
    user_id, equipment_id = setup_records

    response = client.post("/api/maintenance-requests", json={
        "title": "Pump fault",
        "description": "Pump making noise",
        "priority": "critical",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    assert response.status_code == 400
    assert response.json["error"] == "Invalid priority"


def test_create_maintenance_request_with_invalid_user(client):
    response = client.post("/api/maintenance-requests", json={
        "title": "Pump fault",
        "description": "Pump making noise",
        "user_id": 999,
        "equipment_id": 999
    })

    assert response.status_code == 404
    assert response.json["error"] == "User not found"


def test_create_maintenance_request_with_invalid_equipment(
    client, setup_records
):
    user_id, equipment_id = setup_records

    response = client.post("/api/maintenance-requests", json={
        "title": "Pump fault",
        "description": "Pump making noise",
        "user_id": user_id,
        "equipment_id": 999
    })

    assert response.status_code == 404
    assert response.json["error"] == "Equipment not found"


def test_update_maintenance_request(client, setup_records):
    user_id, equipment_id = setup_records

    create_response = client.post("/api/maintenance-requests", json={
        "title": "Pump fault",
        "description": "Pump making noise",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    request_id = create_response.json["id"]

    response = client.put(
        f"/api/maintenance-requests/{request_id}",
        json={
            "priority": "urgent",
            "status": "in_progress"
        }
    )

    assert response.status_code == 200
    assert response.json["priority"] == "urgent"
    assert response.json["status"] == "in_progress"


def test_update_maintenance_request_with_invalid_status(
    client, setup_records
):
    user_id, equipment_id = setup_records

    create_response = client.post("/api/maintenance-requests", json={
        "title": "Pump fault",
        "description": "Pump making noise",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    request_id = create_response.json["id"]

    response = client.put(
        f"/api/maintenance-requests/{request_id}",
        json={"status": "completed"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid status"


def test_delete_maintenance_request(client, setup_records):
    user_id, equipment_id = setup_records

    create_response = client.post("/api/maintenance-requests", json={
        "title": "Temporary fault",
        "description": "Temporary test request",
        "user_id": user_id,
        "equipment_id": equipment_id
    })

    request_id = create_response.json["id"]

    delete_response = client.delete(
        f"/api/maintenance-requests/{request_id}"
    )

    get_response = client.get(
        f"/api/maintenance-requests/{request_id}"
    )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
