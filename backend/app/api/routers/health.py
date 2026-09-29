from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.models.envelope import Envelope

router = APIRouter(tags=["health"])

class HealthStatus(BaseModel):
    status: str
    version: str
    ai_provider: str
    ai_configured: bool
    db_ok: bool

@router.get("/health", response_model=Envelope[HealthStatus])
def get_health():
    # Return a basic health status matching frontend expectations
    # (frontend expects status, version, ai_provider, ai_configured, db_ok)
    return Envelope(
        success=True,
        data=HealthStatus(
            status="ok",
            version="1.0.0",
            ai_provider="backend",
            ai_configured=True,
            db_ok=True
        )
    )
