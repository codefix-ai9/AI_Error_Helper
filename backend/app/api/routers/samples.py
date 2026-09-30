"""
Samples endpoint (§5.5):
  GET /api/v1/samples — serves data/sample_errors.json
"""
import json
from pathlib import Path
from fastapi import APIRouter
from backend.app.models.envelope import Envelope

router = APIRouter(tags=["samples"])

_SAMPLES_PATH = Path(__file__).parents[5] / "data" / "sample_errors.json"


@router.get("/samples", response_model=Envelope[list])
def get_samples():
    if _SAMPLES_PATH.exists():
        data = json.loads(_SAMPLES_PATH.read_text(encoding="utf-8"))
    else:
        data = []
    return Envelope(success=True, data=data)
