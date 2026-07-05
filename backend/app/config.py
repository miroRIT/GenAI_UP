from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "CivicIQ"
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    knowledge_base_dir: Path = Path(__file__).resolve().parents[1] / "knowledge_base"
    geojson_dir: Path = Path(__file__).resolve().parent / "geojson"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./civiciq.db")
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    port: int = int(os.getenv("PORT", "8000"))
    mock_mode: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    news_api_key: str | None = os.getenv("NEWS_API_KEY")
    openweather_api_key: str | None = os.getenv("OPENWEATHER_API_KEY")
    google_maps_api_key: str | None = os.getenv("GOOGLE_MAPS_API_KEY")
    tomtom_api_key: str | None = os.getenv("TOMTOM_API_KEY")
    mapbox_access_token: str | None = os.getenv("MAPBOX_ACCESS_TOKEN")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    enable_scheduler: bool = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    news_refresh_minutes: int = int(os.getenv("NEWS_REFRESH_MINUTES", "30"))
    weather_refresh_minutes: int = int(os.getenv("WEATHER_REFRESH_MINUTES", "30"))
    traffic_refresh_minutes: int = int(os.getenv("TRAFFIC_REFRESH_MINUTES", "15"))
    risk_refresh_minutes: int = int(os.getenv("RISK_REFRESH_MINUTES", "30"))
    alert_refresh_minutes: int = int(os.getenv("ALERT_REFRESH_MINUTES", "30"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
