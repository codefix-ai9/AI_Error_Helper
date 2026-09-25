import pytest
from backend.app.validation.request_validator import validate_analyze_request
from backend.app.core.errors import ValidationException
from backend.app.core.config import settings

def test_validation_language_missing():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"source_code": "print(1)", "error_input": "error"})
    assert exc.value.message == "Please select a programming language."

def test_validation_language_unsupported():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"language": "ruby", "source_code": "print(1)", "error_input": "error"})
    assert exc.value.message == "Language 'ruby' is not supported yet. Supported: python, java, javascript."

def test_validation_source_code_blank():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"language": "python", "source_code": "   \n", "error_input": "error"})
    assert exc.value.message == "Please provide the source code before analysis."

def test_validation_error_input_blank():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"language": "python", "source_code": "print(1)", "error_input": ""})
    assert exc.value.message == "Please provide the compiler/runtime error or observed problem."

def test_validation_max_source_size():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"language": "python", "source_code": "a" * (settings.MAX_SOURCE_CHARS + 1), "error_input": "error"})
    assert f"max {settings.MAX_SOURCE_CHARS:,} characters" in exc.value.message

def test_validation_max_error_size():
    with pytest.raises(ValidationException) as exc:
        validate_analyze_request({"language": "python", "source_code": "print(1)", "error_input": "a" * (settings.MAX_ERROR_CHARS + 1)})
    assert f"max {settings.MAX_ERROR_CHARS:,} characters" in exc.value.message
