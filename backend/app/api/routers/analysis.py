from fastapi import APIRouter, Depends
from backend.app.models.requests import AnalyzeRequest
from backend.app.models.responses import AnalysisResult
from backend.app.models.envelope import Envelope
from backend.app.application.ports import AnalysisServicePort
from backend.app.application.container import get_analysis_service
from backend.app.core.config import settings, Settings

router = APIRouter(tags=["analysis"])

def get_service() -> AnalysisServicePort:
    return get_analysis_service(settings)

@router.post("/analyze", response_model=Envelope[AnalysisResult])
def analyze_code(
    request: AnalyzeRequest,
    service: AnalysisServicePort = Depends(get_service)
):
    result = service.analyze(request)
    return Envelope(success=True, data=result)
