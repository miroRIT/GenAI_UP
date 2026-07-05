from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(80), index=True)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    district_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    assigned_districts: Mapped[str] = mapped_column(Text, default="[]")
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(40), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    district_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    priority: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(40), default="New", index=True)
    assigned_department: Mapped[str] = mapped_column(String(120), default="District Administration")
    source: Mapped[str] = mapped_column(String(120), default="CivicIQ")
    recommended_actions: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[str] = mapped_column(Text, default="")
    incident_brief: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_status: Mapped[str] = mapped_column(String(40), default="On Track")
    first_response_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    escalation_status: Mapped[str] = mapped_column(String(80), default="None")


class AlertTimelineEvent(Base):
    __tablename__ = "alert_timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(40), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    actor: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IngestionJobLog(Base):
    __tablename__ = "ingestion_job_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_name: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, default="")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    triggered_by: Mapped[str] = mapped_column(String(120), default="system")


class Incident(Base):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    district_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    source: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProviderStatus(Base):
    __tablename__ = "provider_status"

    provider_name: Mapped[str] = mapped_column(String(80), primary_key=True)
    provider_type: Mapped[str] = mapped_column(String(80), index=True)
    configured: Mapped[int] = mapped_column(Integer, default=0)
    health_status: Mapped[str] = mapped_column(String(40), default="unknown")
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str] = mapped_column(Text, default="")
    rate_limit_status: Mapped[str] = mapped_column(String(120), default="unknown")


class ProviderObservation(Base):
    __tablename__ = "provider_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(80), index=True)
    provider_type: Mapped[str] = mapped_column(String(80), index=True)
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    district_name: Mapped[str] = mapped_column(String(255))
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source_url: Mapped[str] = mapped_column(Text, default="")
    raw_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    normalized_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    confidence: Mapped[float] = mapped_column(Float, default=0.65)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(80))
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    temperature: Mapped[float] = mapped_column(Float, default=0)
    feels_like: Mapped[float] = mapped_column(Float, default=0)
    humidity: Mapped[float] = mapped_column(Float, default=0)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0)
    wind_speed: Mapped[float] = mapped_column(Float, default=0)
    condition: Mapped[str] = mapped_column(String(120), default="")
    heat_index: Mapped[float] = mapped_column(Float, default=0)
    forecast_date: Mapped[str] = mapped_column(String(40), default="")
    raw_observation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class TrafficObservation(Base):
    __tablename__ = "traffic_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(80))
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    route_name: Mapped[str] = mapped_column(String(255), default="")
    congestion_level: Mapped[float] = mapped_column(Float, default=0)
    average_speed_kmph: Mapped[float] = mapped_column(Float, default=0)
    travel_time_delay_minutes: Mapped[float] = mapped_column(Float, default=0)
    incident_count: Mapped[int] = mapped_column(Integer, default=0)
    road_closure_count: Mapped[int] = mapped_column(Integer, default=0)
    latitude: Mapped[float] = mapped_column(Float, default=0)
    longitude: Mapped[float] = mapped_column(Float, default=0)
    raw_observation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class NewsObservation(Base):
    __tablename__ = "news_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(80))
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(Text, default="")
    source_name: Mapped[str] = mapped_column(String(120), default="")
    category: Mapped[str] = mapped_column(String(80), default="")
    severity: Mapped[str] = mapped_column(String(40), default="")
    inferred_latitude: Mapped[float] = mapped_column(Float, default=0)
    inferred_longitude: Mapped[float] = mapped_column(Float, default=0)
    raw_observation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AQIObservation(Base):
    __tablename__ = "aqi_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(80))
    district_id: Mapped[str] = mapped_column(String(40), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    aqi: Mapped[float] = mapped_column(Float, default=0)
    pm25: Mapped[float] = mapped_column(Float, default=0)
    pm10: Mapped[float] = mapped_column(Float, default=0)
    category: Mapped[str] = mapped_column(String(80), default="")
    health_advisory: Mapped[str] = mapped_column(Text, default="")
    raw_observation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AlertNote(Base):
    __tablename__ = "alert_notes"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(40), index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note_text: Mapped[str] = mapped_column(Text)
    note_type: Mapped[str] = mapped_column(String(80), default="Note")
    visibility: Mapped[str] = mapped_column(String(80), default="Internal")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BoundarySource(Base):
    __tablename__ = "boundary_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(Text, default="")
    license: Mapped[str] = mapped_column(String(255), default="Unknown")
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    boundary_level: Mapped[str] = mapped_column(String(80), default="district")
    state: Mapped[str] = mapped_column(String(120), default="NCR")
    district_name: Mapped[str] = mapped_column(String(255), default="")
    file_path: Mapped[str] = mapped_column(Text)
    is_official: Mapped[int] = mapped_column(Integer, default=0)
