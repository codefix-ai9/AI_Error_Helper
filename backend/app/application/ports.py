from typing import Protocol
from backend.app.models.requests import AnalyzeRequest
from backend.app.models.responses import AnalysisResult
from backend.app.models.stages import AIRequestContext, AIOutcome

class AIEnginePort(Protocol):
    def explain(self, ctx: AIRequestContext) -> AIOutcome:
        """Analyze the context and return AI explanation and suggestions. NEVER raises."""
        ...

class HistoryPort(Protocol):
    def save(self, result: AnalysisResult) -> bool:
        """Save analysis result. Returns False on storage failure; NEVER raises."""
        ...

class AnalysisServicePort(Protocol):
    def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
        """Orchestrates the analysis pipeline."""
        ...
