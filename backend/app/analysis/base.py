from typing import Protocol, List
from backend.app.models.stages import NormalizedInput, Finding

class LanguageAnalyzer(Protocol):
    def analyze(self, input_data: NormalizedInput) -> List[Finding]:
        ...
