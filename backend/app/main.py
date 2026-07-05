from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import analytics, chat, health, overview, recommendations, upload, wards
from app.services.data_loader import ensure_sample_data
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


@app.on_event("startup")
def startup() -> None:
    ensure_sample_data()
    ensure_knowledge_base()
