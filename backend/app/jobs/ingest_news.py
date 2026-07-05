from app.services.provider_service import fetch_news_items


def run() -> int:
    return len(fetch_news_items())
