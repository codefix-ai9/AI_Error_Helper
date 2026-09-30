"""
AI output schema (§7.3). Validated strictly before use.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class AIExplanation(BaseModel):
    """Structured AI explanation returned by the provider and validated."""
    explanation: str = Field(..., max_length=1500)
    probable_cause: str
    affected_code: Optional[str] = None
    corrected_code: Optional[str] = None
    debugging_steps: List[str] = Field(..., min_length=3, max_length=8)
    prevention_tip: str
    key_concept: str
    uncertainty_note: str
    suggested_category: Optional[str] = None  # Only used when static result is Unknown
