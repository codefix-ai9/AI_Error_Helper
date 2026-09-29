from fastapi import APIRouter
from backend.app.models.envelope import Envelope
from backend.app.models.enums import Language
from typing import List

router = APIRouter(tags=["languages"])

@router.get("/languages", response_model=Envelope[List[str]])
def get_languages():
    languages = [lang.value for lang in Language]
    return Envelope(success=True, data=languages)
