import re
from typing import List, Optional
from backend.app.models.stages import ErrorRecord, Location

def classify_and_split(error_text: str) -> List[ErrorRecord]:
    # Placeholder for actual parsing logic
    # For now, treat the entire error text as a single record
    return [
        ErrorRecord(
            original_text=error_text,
            error_type=None,
            message=error_text,
            frame_location=None
        )
    ]
