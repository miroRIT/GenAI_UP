from app.services.disaster_risk_engine import calculate_disaster_risk


def run() -> int:
    return len(calculate_disaster_risk())
