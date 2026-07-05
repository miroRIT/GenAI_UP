from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "CivicIQ"
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    knowledge_base_dir: Path = Path(__file__).resolve().parents[1] / "knowledge_base"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
