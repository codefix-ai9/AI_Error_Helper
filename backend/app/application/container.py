from backend.app.core.config import Settings
from backend.app.application.ports import AIEnginePort, HistoryPort

def build_ai_engine(settings: Settings) -> AIEnginePort:
    from backend.app.ai.engine import build_ai_engine as factory
    return factory(settings)

def build_history_repository(settings: Settings) -> HistoryPort:
    from backend.app.history.repository import build_history_repository as factory
    return factory(settings)
