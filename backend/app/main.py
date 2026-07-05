from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.jobs.scheduler import start_scheduler
from app.routes import alerts, analytics, auth, chat, disaster_risk, districts, health, jobs, monitoring, observations, overview, providers, recommendations, upload, wards
from app.services.data_loader import ensure_sample_data
from app.services.alert_service import seed_alerts
from app.services.auth_service import seed_demo_users
from app.services.geospatial_service import ensure_geojson
from app.services.rag_engine import ensure_knowledge_base


settings = get_settings()

app = FastAPI(
    title="CivicIQ API",
    description="AI Decision Intelligence Platform for Community Well-being.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(overview.router, prefix="/api")
app.include_router(wards.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(districts.router, prefix="/api")
app.include_router(disaster_risk.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(observations.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    ensure_sample_data()
    ensure_knowledge_base()
    ensure_geojson()
    init_db()
    db = SessionLocal()
    try:
        seed_demo_users(db)
        seed_alerts(db)
    finally:
        db.close()
    start_scheduler()
