from fastapi.testclient import TestClient

from app.main import app
from app.services.alert_service import create_alert, transition_alert
from app.services.disaster_risk_engine import calculate_disaster_risk
from app.services.provider_service import fallback_news, fallback_weather
from app.database import SessionLocal, init_db
from app.services.auth_service import seed_demo_users
from app.models.db_models import Alert


client = TestClient(app)


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
