from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.database import SessionLocal
from app.services.job_service import run_job


scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    settings = get_settings()
    if not settings.enable_scheduler or scheduler.running:
        return

    schedules = {
        "news": settings.news_refresh_minutes,
        "weather": settings.weather_refresh_minutes,
        "traffic": settings.traffic_refresh_minutes,
        "risk": settings.risk_refresh_minutes,
        "alerts": settings.alert_refresh_minutes,
    }
    for job_name, minutes in schedules.items():
        scheduler.add_job(_run_scheduled_job, "interval", minutes=minutes, args=[job_name], id=job_name, replace_existing=True)
    scheduler.start()


def _run_scheduled_job(job_name: str) -> None:
    db = SessionLocal()
    try:
        run_job(db, job_name)
    finally:
        db.close()
