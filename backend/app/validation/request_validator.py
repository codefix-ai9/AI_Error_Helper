from typing import Any
from backend.app.models.enums import Language
from backend.app.core.config import settings
from backend.app.core.errors import ValidationException
from backend.app.models.envelope import ErrorDetail

def validate_analyze_request(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
        
    # language required
    if 'language' not in data or not data['language']:
        raise ValidationException("Please select a programming language.", [ErrorDetail(field="language", message="Missing")])
        
    # language supported
    try:
        Language(data['language'])
    except ValueError:
        raise ValidationException(f"Language '{data['language']}' is not supported yet. Supported: python, java, javascript.", [ErrorDetail(field="language", message="Unsupported")])
        
    # source_code non-blank
    if 'source_code' not in data or not data['source_code'].strip():
        raise ValidationException("Please provide the source code before analysis.", [ErrorDetail(field="source_code", message="Missing")])
        
    # error_input non-blank
    if 'error_input' not in data or not data['error_input'].strip():
        raise ValidationException("Please provide the compiler/runtime error or observed problem.", [ErrorDetail(field="error_input", message="Missing")])
        
    # max source size
    if len(data['source_code']) > settings.MAX_SOURCE_CHARS:
        raise ValidationException(f"Source code is too large (max {settings.MAX_SOURCE_CHARS:,} characters).", [ErrorDetail(field="source_code", message="Too large")])
        
    # max error size
    if len(data['error_input']) > settings.MAX_ERROR_CHARS:
        raise ValidationException(f"Error text is too large (max {settings.MAX_ERROR_CHARS:,} characters).", [ErrorDetail(field="error_input", message="Too large")])
        
    return data
