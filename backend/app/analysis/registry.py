from typing import Dict, Protocol, List
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
        raise ValueError(f"No analyzer registered for {language}")
    return _registry[language]

def get_supported_languages() -> List[str]:
    return [lang.value for lang in _registry.keys()]
