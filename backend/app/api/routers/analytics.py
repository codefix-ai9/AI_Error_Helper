"""
Analytics endpoint (§5.5, §9):
  GET /api/v1/analytics/summary
"""
from fastapi import APIRouter, Depends
from backend.app.models.envelope import Envelope
from backend.app.history.repository import SQLiteHistoryRepository
from backend.app.application.container import build_history_repository
from backend.app.core.config import settings

router = APIRouter(tags=["analytics"])


def _get_repo() -> SQLiteHistoryRepository:
    return build_history_repository(settings)


@router.get("/analytics/summary", response_model=Envelope[dict])
def analytics_summary(repo: SQLiteHistoryRepository = Depends(_get_repo)):
    data = repo.analytics_summary()
    return Envelope(success=True, data=data)
