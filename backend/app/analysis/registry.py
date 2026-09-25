from typing import Dict, Protocol, List
import logging
from backend.app.models.stages import NormalizedInput, Finding
from backend.app.models.enums import Language

class LanguageAnalyzer(Protocol):
    def analyze(self, input_data: NormalizedInput) -> List[Finding]:
        ...

_registry: Dict[Language, LanguageAnalyzer] = {}

def register_analyzer(language: Language, analyzer: LanguageAnalyzer):
    _registry[language] = analyzer

def get_analyzer(language: Language) -> LanguageAnalyzer:
    if language not in _registry:
        # Graceful degradation for unsupported languages (Java/JS skipped per A-M4 fast-mode)
        logging.getLogger(__name__).warning(f"No fully implemented analyzer for {language}. Defaulting to graceful degradation.")
        
        class FallbackAnalyzer(LanguageAnalyzer):
            def analyze(self, input_data: NormalizedInput) -> List[Finding]:
                return []
                
        return FallbackAnalyzer()
    return _registry[language]

def get_supported_languages() -> List[str]:
    # Hardcode python as the only officially supported for now
    return [Language.PYTHON.value]
