from app.services.provider_service import fetch_traffic_observations


def run() -> int:
    return len(fetch_traffic_observations())
