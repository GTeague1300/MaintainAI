import pytest

from app.extensions import db
from app.models import User, Equipment, MaintenanceRequest, WorkOrder


@pytest.fixture
def setup_records(app):
    with app.app_context():
        reporter = User(
            email="reporter@test.com",
            password_hash="test_hash",
            first_name="Test",
            last_name="Reporter",
            role="reporter"
        )

        engineer = User(
            email="engineer@test.com",
            password_hash="test_hash",
            first_name="Test",
            last_name="Engineer",
            role="engineer"
        )

        equipment = Equipment(
            name="Industrial Pump",
            description="Test pump",
            serial_number="PUMP-001",
            location="Factory",
            status="operational"
        )

        db.session.add_all([reporter, engineer, equipment])
        db.session.commit()

        maintenance_request = MaintenanceRequest(
            title="Pump making noise",
            description="Unusual noise coming from the pump",
            priority="high",
            status="open",
            user_id=reporter.id,
            equipment_id=equipment.id
        )

        db.session.add(maintenance_request)
        db.session.commit()

        return {
            "reporter_id": reporter.id,
            "engineer_id": engineer.id,
            "maintenance_request_id": maintenance_request.id
        }

def test_get_work_orders_empty(client):
    response = client.get("/api/work-orders/")

    assert response.status_code == 200
    assert response.json == []


def test_create_work_order(client, setup_records):
    response = client.post("/api/work-orders/", json={
        "title": "Inspect industrial pump",
        "description": "Investigate the unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"],
        "assigned_to": setup_records["engineer_id"]
    })

    assert response.status_code == 201
    assert response.json["work_order"]["title"] == "Inspect industrial pump"
    assert response.json["work_order"]["status"] == "assigned"
    assert response.json["work_order"]["assigned_to"] == setup_records["engineer_id"]


def test_create_work_order_without_engineer(client, setup_records):
    response = client.post("/api/work-orders/", json={
        "title": "Inspect industrial pump",
        "description": "Investigate the unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    assert response.status_code == 201
    assert response.json["work_order"]["status"] == "open"
    assert response.json["work_order"]["assigned_to"] is None


def test_create_work_order_invalid_request(client):
    response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Test description",
        "maintenance_request_id": 999
    })

    assert response.status_code == 404


def test_create_work_order_invalid_engineer(client, setup_records):
    response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Test description",
        "maintenance_request_id": setup_records["maintenance_request_id"],
        "assigned_to": setup_records["reporter_id"]
    })

    assert response.status_code == 400

def test_get_work_order(client, setup_records):
    create_response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Investigate unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    work_order_id = create_response.json["work_order"]["id"]

    response = client.get(f"/api/work-orders/{work_order_id}")

    assert response.status_code == 200
    assert response.json["title"] == "Inspect pump"


def test_get_work_order_not_found(client):
    response = client.get("/api/work-orders/999")

    assert response.status_code == 404


def test_update_work_order(client, setup_records):
    create_response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Investigate unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    work_order_id = create_response.json["work_order"]["id"]

    response = client.put(
        f"/api/work-orders/{work_order_id}",
        json={
            "status": "in_progress",
            "title": "Repair industrial pump"
        }
    )

    assert response.status_code == 200
    assert response.json["work_order"]["title"] == "Repair industrial pump"
    assert response.json["work_order"]["status"] == "in_progress"


def test_complete_work_order(client, setup_records):
    create_response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Investigate unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    work_order_id = create_response.json["work_order"]["id"]

    response = client.put(
        f"/api/work-orders/{work_order_id}",
        json={"status": "completed"}
    )

    assert response.status_code == 200
    assert response.json["work_order"]["completed_at"] is not None


def test_update_work_order_invalid_status(client, setup_records):
    create_response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Investigate unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    work_order_id = create_response.json["work_order"]["id"]

    response = client.put(
        f"/api/work-orders/{work_order_id}",
        json={"status": "invalid"}
    )

    assert response.status_code == 400


def test_delete_work_order(client, setup_records):
    create_response = client.post("/api/work-orders/", json={
        "title": "Inspect pump",
        "description": "Investigate unusual noise",
        "maintenance_request_id": setup_records["maintenance_request_id"]
    })

    work_order_id = create_response.json["work_order"]["id"]

    response = client.delete(f"/api/work-orders/{work_order_id}")

    assert response.status_code == 200

    get_response = client.get(f"/api/work-orders/{work_order_id}")

    assert get_response.status_code == 404