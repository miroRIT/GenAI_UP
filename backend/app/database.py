from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()


def _ensure_sqlite_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "alerts" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("alerts")}
    alert_columns = {
        "sla_due_at": "DATETIME",
        "sla_status": "VARCHAR(40) DEFAULT 'On Track'",
        "first_response_due_at": "DATETIME",
        "resolution_due_at": "DATETIME",
        "escalation_status": "VARCHAR(80) DEFAULT 'None'",
    }
    user_columns = {
        "department": "VARCHAR(120)",
        "assigned_districts": "TEXT DEFAULT '[]'",
        "is_active": "INTEGER DEFAULT 1",
    }
    job_columns = {
        "retry_count": "INTEGER DEFAULT 0",
        "duration_ms": "INTEGER DEFAULT 0",
        "triggered_by": "VARCHAR(120) DEFAULT 'system'",
    }

    with engine.begin() as connection:
        for column_name, column_type in alert_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE alerts ADD COLUMN {column_name} {column_type}"))
        if "users" in inspector.get_table_names():
            user_existing = {column["name"] for column in inspector.get_columns("users")}
            for column_name, column_type in user_columns.items():
                if column_name not in user_existing:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
        if "ingestion_job_logs" in inspector.get_table_names():
            job_existing = {column["name"] for column in inspector.get_columns("ingestion_job_logs")}
            for column_name, column_type in job_columns.items():
                if column_name not in job_existing:
                    connection.execute(text(f"ALTER TABLE ingestion_job_logs ADD COLUMN {column_name} {column_type}"))
