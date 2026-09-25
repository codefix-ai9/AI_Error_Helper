from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.app.models.enums import Language, ErrorType, Severity, AIStatus
from backend.app.models.stages import Location, Finding, AISuggestion, CorrectionDiff

class Verification(BaseModel):
    corrected_code_parses: bool = False
    original_finding_resolved: bool = False
    note: str = "Passes syntax/static re-check. This is NOT proof of correct behavior."

class AnalysisMetadata(BaseModel):
    analysis_mode: str = "hybrid"  # "hybrid" or "static_only"
    pipeline_version: str = "1.0"
    prompt_version: str = ""
    provider: str = ""
    model: str = ""
    ai_latency_ms: int = 0
    analyzers_run: List[str] = Field(default_factory=list)
    analyzer_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    history_saved: bool = False

class AnalysisResult(BaseModel):
    schema_version: str = "1.0"
    analysis_id: str
    created_at: str
    language: Language
    error_type: ErrorType
    severity: Severity
    location: Optional[Location] = None
    summary: str
    explanation: Optional[str] = None
    probable_cause: Optional[str] = None
    affected_code: Optional[str] = None
    corrected_code: Optional[str] = None
    correction_diff: Optional[CorrectionDiff] = None
    debugging_steps: List[str] = Field(default_factory=list)
    prevention_tip: Optional[str] = None
    key_concept: Optional[str] = None
    confidence: Optional[float] = None
    confidence_basis: List[str] = Field(default_factory=list)
    uncertainty_note: Optional[str] = None
    static_findings: List[Finding] = Field(default_factory=list)
    ai_suggestions: List[AISuggestion] = Field(default_factory=list)
    practice_exercise: Optional[str] = None
    quiz_question: Optional[str] = None
    verification: Optional[Verification] = None
    provenance: Dict[str, str] = Field(default_factory=dict)
    ai_status: AIStatus
    analysis_metadata: AnalysisMetadata

class HistoryItem(BaseModel):
    analysis_id: str
    created_at: str
    language: Language
    error_type: ErrorType
    severity: Severity
    summary: str

class AnalyticsSummary(BaseModel):
    total_analyses: int = 0
    errors_by_type: Dict[str, int] = Field(default_factory=dict)
    errors_by_language: Dict[str, int] = Field(default_factory=dict)
