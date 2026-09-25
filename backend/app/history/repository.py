from backend.app.application.ports import HistoryPort
from backend.app.models.responses import AnalysisResult
from backend.app.core.config import Settings

class InMemoryHistoryRepository(HistoryPort):
    def save(self, result: AnalysisResult) -> bool:
        return True

def build_history_repository(settings: Settings) -> HistoryPort:
    return InMemoryHistoryRepository()
