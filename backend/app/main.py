from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.logging import setup_logging
from backend.app.api.routers import analysis, health, languages

setup_logging()

app = FastAPI(title="AI Error Helper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(languages.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
