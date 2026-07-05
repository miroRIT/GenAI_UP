from app.services.provider_service import fetch_weather_observations


def run() -> int:
    return len(fetch_weather_observations())
