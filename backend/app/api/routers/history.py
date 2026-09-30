"""
History endpoints (§5.5):
  GET  /api/v1/history              list with filters/pagination
  GET  /api/v1/history/{id}         full stored result
  DELETE /api/v1/history/{id}       delete one record
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from backend.app.models.envelope import Envelope, ErrorResponse
from backend.app.models.responses import AnalysisResult, HistoryItem
from backend.app.history.repository import SQLiteHistoryRepository
from backend.app.application.container import build_history_repository
from backend.app.core.config import settings
import uuid

router = APIRouter(tags=["history"])


def _get_repo() -> SQLiteHistoryRepository:
    return build_history_repository(settings)


@router.get("/history", response_model=Envelope[dict])
def list_history(
    q: Optional[str] = Query(None, description="Search in summary, error_type, language"),
    language: Optional[str] = Query(None),
    error_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: SQLiteHistoryRepository = Depends(_get_repo),
):
    items, total = repo.list_items(
        q=q, language=language, error_type=error_type,
        severity=severity, limit=limit, offset=offset
    )
    return Envelope(
        success=True,
        data={
            "items": [i.model_dump() for i in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@router.get("/history/{analysis_id}", response_model=Envelope[AnalysisResult])
def get_history_item(
    analysis_id: str,
    repo: SQLiteHistoryRepository = Depends(_get_repo),
):
    result = repo.get_by_id(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Envelope(success=True, data=result)


@router.delete("/history/{analysis_id}", response_model=Envelope[dict])
def delete_history_item(
    analysis_id: str,
    repo: SQLiteHistoryRepository = Depends(_get_repo),
):
    deleted = repo.delete_by_id(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return Envelope(success=True, data={"deleted": analysis_id})
