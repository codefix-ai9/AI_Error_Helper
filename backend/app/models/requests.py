from pydantic import BaseModel, Field
from typing import Optional
from backend.app.models.enums import Language

class AnalyzeRequest(BaseModel):
    language: Language = Field(..., description="Programming language of the source code")
    source_code: str = Field(..., description="Source code to analyze")
    error_input: str = Field(..., description="Compiler/runtime error or observed problem")
    expected_behavior: Optional[str] = Field(None, description="Optional free text describing expected behavior")
