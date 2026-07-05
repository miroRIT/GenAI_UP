from fastapi.testclient import TestClient

from app.main import app
from app.services.alert_service import create_alert, transition_alert
from app.services.disaster_risk_engine import calculate_disaster_risk
from app.services.observation_service import persist_provider_records
from app.services.provider_service import fallback_news, fallback_weather
from app.database import SessionLocal, init_db
from app.services.auth_service import seed_demo_users
from app.models.db_models import Alert


client = TestClient(app)


def auth_headers(email: str = "admin@civiciq.demo", password: str = "Admin@12345") -> dict[str, str]:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_disaster_risk_calculation():
    risks = calculate_disaster_risk()
    assert risks
    assert "overall" in risks[0]
    assert 0 <= risks[0]["overall"]["score"] <= 100


def test_provider_fallback_behavior():
    assert fallback_news()
    assert fallback_weather()


def test_auth_login():
    init_db()
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@civiciq.demo", "password": "Admin@12345"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "Admin"
    assert response.json()["user"]["department"] == "Platform Operations"


def test_alert_status_transition():
    init_db()
    db = SessionLocal()
    try:
        alert = create_alert(
            db,
            {
                "title": "Test flood alert",
                "description": "Testing alert transition",
                "district_id": "NCR01",
                "district_name": "Delhi NCT",
                "category": "Flood",
                "severity": "High",
                "recommended_actions": ["Verify pumps"],
            },
        )
        updated = transition_alert(db, db.get(Alert, alert["alert_id"]), "Acknowledged")
        assert updated["status"] == "Acknowledged"
    finally:
        db.close()


def test_job_run_requires_auth_and_allows_admin():
    response = client.post("/api/jobs/run/risk")
    assert response.status_code == 401

    response = client.post("/api/jobs/run/risk", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["status"] == "Success"


def test_viewer_cannot_run_jobs():
    response = client.post(
        "/api/jobs/run/risk",
        headers=auth_headers("viewer@civiciq.demo", "Viewer@12345"),
    )
    assert response.status_code == 403


def test_provider_status_endpoint():
    init_db()
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    providers = response.json()
    assert any(provider["provider_type"] == "weather" for provider in providers)


def test_provider_smoke_requires_permission():
    response = client.post("/api/providers/test/geospatial")
    assert response.status_code == 401

    response = client.post("/api/providers/test/geospatial", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["records_processed"] >= 1


def test_alert_pdf_export_and_assigned_alerts():
    init_db()
    db = SessionLocal()
    try:
        created = create_alert(
            db,
            {
                "title": "Fire response test",
                "description": "Testing PDF export",
                "district_id": "NCR01",
                "district_name": "Delhi NCT",
                "category": "Fire/Industrial",
                "severity": "High",
                "assigned_department": "Fire Department",
                "recommended_actions": ["Dispatch field verification"],
            },
        )
    finally:
        db.close()

    department_headers = auth_headers("department@civiciq.demo", "Department@12345")
    assigned = client.get("/api/alerts/assigned-to-me", headers=department_headers)
    assert assigned.status_code == 200
    assert any(alert["alert_id"] == created["alert_id"] for alert in assigned.json())

    pdf = client.get(f"/api/alerts/{created['alert_id']}/export.pdf", headers=department_headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")


def test_observation_persistence_and_listing():
    init_db()
    db = SessionLocal()
    try:
        count = persist_provider_records(
            db,
            "UnitTestWeather",
            "weather",
            [
                {
                    "district_id": "NCR01",
                    "district_name": "Delhi NCT",
                    "temperature": 34,
                    "feels_like": 39,
                    "humidity": 55,
                    "rainfall_mm": 8,
                    "condition": "Humid",
                }
            ],
        )
    finally:
        db.close()
    assert count == 1

    response = client.get("/api/observations?type=weather&district_id=NCR01")
    assert response.status_code == 200
    assert any(item["provider_name"] == "UnitTestWeather" for item in response.json())
