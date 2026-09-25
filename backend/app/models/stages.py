from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.app.models.enums import Language, ErrorType, Severity, EvidenceLevel, AIStatus, Provenance

class Location(BaseModel):
    line: Optional[int] = None
    column: Optional[int] = None
    end_line: Optional[int] = None

class ErrorRecord(BaseModel):
    original_text: str
    error_type: Optional[str] = None
    message: Optional[str] = None
    frame_location: Optional[Location] = None

class RedactionReport(BaseModel):
    redacted_items: int = 0
    patterns_used: List[str] = Field(default_factory=list)

class NormalizedInput(BaseModel):
    language: Language
    source_code: str
    error_records: List[ErrorRecord] = Field(default_factory=list)
    error_text_clean: str
    redaction_report: RedactionReport
    expected_behavior: Optional[str] = None

class Finding(BaseModel):
    rule_id: str
    category: str
    evidence_level: EvidenceLevel
    source: str
    message: str
    location: Location
    snippet: Optional[str] = None
    concept: Optional[str] = None

class StaticAnalysisResult(BaseModel):
    findings: List[Finding] = Field(default_factory=list)
    primary_finding: Optional[Finding] = None
    error_type: ErrorType = ErrorType.UNKNOWN
    severity: Severity = Severity.UNKNOWN
    location: Optional[Location] = None
    evidence_level: EvidenceLevel = EvidenceLevel.NONE
    corroborated: bool = False
    analyzers_run: List[str] = Field(default_factory=list)
    analyzer_errors: List[str] = Field(default_factory=list)

class AIRequestContext(BaseModel):
    static_result: StaticAnalysisResult
    normalized_input: NormalizedInput

class AISuggestion(BaseModel):
    kind: str  # e.g., explanation, correction, debug_step, prevention, suggested_category, practice_exercise, quiz_question
    text: str
    provenance: str = "ai"

class AIOutcome(BaseModel):
    status: AIStatus
    payload: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: int = 0
    repair_attempts: int = 0
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[AISuggestion] = Field(default_factory=list)
    practice_exercise: Optional[str] = None
    quiz_question: Optional[str] = None

class CorrectionDiff(BaseModel):
    changed_lines_before: List[int] = Field(default_factory=list)
    changed_lines_after: List[int] = Field(default_factory=list)
    unified: str = ""

class Recommendation(BaseModel):
    error_type: ErrorType
    severity: Severity
    location: Optional[Location]
    summary: str
    explanation: Optional[str] = None
    probable_cause: Optional[str] = None
    affected_code: Optional[str] = None
    corrected_code: Optional[str] = None
    debugging_steps: List[str] = Field(default_factory=list)
    prevention_tip: Optional[str] = None
    key_concept: Optional[str] = None
    confidence: Optional[float] = None
    confidence_basis: List[str] = Field(default_factory=list)
    uncertainty_note: Optional[str] = None
    practice_exercise: Optional[str] = None
    quiz_question: Optional[str] = None
    ai_suggestions: List[AISuggestion] = Field(default_factory=list)
    provenance_map: Dict[str, str] = Field(default_factory=dict)
