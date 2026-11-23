from app.extensions import db
from app.models import Equipment, User, MaintenanceRequest


def test_get_all_equipment(client):
    client.post("/api/equipment", json={
        "name": "Test Pump",
        "serial_number": "PUMP-TEST-001"
    })

    response = client.get("/api/equipment")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Test Pump"


def test_get_equipment_by_id(client):
    create_response = client.post("/api/equipment", json={
        "name": "Test Pump",
        "serial_number": "PUMP-TEST-002"
    })

    equipment_id = create_response.json["id"]

    response = client.get(f"/api/equipment/{equipment_id}")

    assert response.status_code == 200
    assert response.json["name"] == "Test Pump"


def test_get_nonexistent_equipment(client):
    response = client.get("/api/equipment/999")

    assert response.status_code == 404
    assert response.json["error"] == "Equipment not found"


def test_create_equipment(client):
    response = client.post("/api/equipment", json={
        "name": "Test Motor",
        "serial_number": "MOTOR-TEST-001"
    })

    assert response.status_code == 201
    assert response.json["name"] == "Test Motor"
    assert response.json["status"] == "operational"


def test_create_equipment_without_name(client):
    response = client.post("/api/equipment", json={
        "serial_number": "PUMP-TEST-003"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Equipment name is required"


def test_create_equipment_with_invalid_status(client):
    response = client.post("/api/equipment", json={
        "name": "Test Pump",
        "status": "broken"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Invalid equipment status"


def test_duplicate_serial_number(client):
    equipment_data = {
        "name": "Test Pump",
        "serial_number": "DUPLICATE-001"
    }

    first_response = client.post(
        "/api/equipment",
        json=equipment_data
    )

    second_response = client.post(
        "/api/equipment",
        json=equipment_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_update_equipment(client):
    create_response = client.post("/api/equipment", json={
        "name": "Old Pump",
        "serial_number": "PUMP-TEST-004"
    })

    equipment_id = create_response.json["id"]

    response = client.put(
        f"/api/equipment/{equipment_id}",
        json={
            "name": "Updated Pump",
            "location": "Factory Floor 2"
        }
    )

    assert response.status_code == 200
    assert response.json["name"] == "Updated Pump"
    assert response.json["location"] == "Factory Floor 2"


def test_update_equipment_with_invalid_status(client):
    create_response = client.post("/api/equipment", json={
        "name": "Test Pump",
        "serial_number": "PUMP-TEST-005"
    })

    equipment_id = create_response.json["id"]

    response = client.put(
        f"/api/equipment/{equipment_id}",
        json={"status": "broken"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid equipment status"


def test_delete_equipment(client):
    create_response = client.post("/api/equipment", json={
        "name": "Temporary Pump",
        "serial_number": "PUMP-TEST-006"
    })

    equipment_id = create_response.json["id"]

    delete_response = client.delete(
        f"/api/equipment/{equipment_id}"
    )

    get_response = client.get(
        f"/api/equipment/{equipment_id}"
    )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_prevent_deleting_equipment_with_maintenance_history(
    app, client
):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash="test-password-hash",
            first_name="Test",
            last_name="User"
        )

        equipment = Equipment(
            name="Maintenance Pump",
            serial_number="PUMP-TEST-007"
        )

        db.session.add_all([user, equipment])
        db.session.commit()

        maintenance_request = MaintenanceRequest(
            title="Pump inspection",
            description="Routine maintenance inspection",
            user_id=user.id,
            equipment_id=equipment.id
        )

        db.session.add(maintenance_request)
        db.session.commit()

        equipment_id = equipment.id

    response = client.delete(
        f"/api/equipment/{equipment_id}"
    )

    assert response.status_code == 409
    assert "maintenance history" in response.json["error"]