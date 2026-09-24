from backend.app.application.ports import AIEnginePort
from backend.app.models.stages import AIRequestContext, AIOutcome
from backend.app.models.enums import AIStatus
from backend.app.core.config import Settings

class NullAIEngine(AIEnginePort):
    def explain(self, ctx: AIRequestContext) -> AIOutcome:
        return AIOutcome(status=AIStatus.DISABLED)

def build_ai_engine(settings: Settings) -> AIEnginePort:
    return NullAIEngine()
