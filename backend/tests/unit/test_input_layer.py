import pytest
from backend.app.models.requests import AnalyzeRequest
from backend.app.models.enums import Language
from backend.app.core.errors import ValidationException
from backend.app.core.config import settings
from backend.app.collector.collector import classify_and_split
from backend.app.preprocessing.preprocessor import preprocess, create_redacted_copy, clean_text
from backend.app.analysis.registry import register_analyzer, get_analyzer, get_supported_languages

def test_validation_language_missing():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"source_code": "print(1)", "error_input": "error"})
    assert exc.value.message == "Please select a programming language."

def test_validation_language_unsupported():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"language": "ruby", "source_code": "print(1)", "error_input": "error"})
    assert exc.value.message == "Language 'ruby' is not supported yet. Supported: python, java, javascript."

def test_validation_source_code_blank():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"language": "python", "source_code": "   \n", "error_input": "error"})
    assert exc.value.message == "Please provide the source code before analysis."

def test_validation_error_input_blank():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"language": "python", "source_code": "print(1)", "error_input": ""})
    assert exc.value.message == "Please provide the compiler/runtime error or observed problem."

def test_validation_max_source_size():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"language": "python", "source_code": "a" * (settings.MAX_SOURCE_CHARS + 1), "error_input": "error"})
    assert f"max {settings.MAX_SOURCE_CHARS:,} characters" in exc.value.message

def test_validation_max_error_size():
    with pytest.raises(ValidationException) as exc:
        AnalyzeRequest.validate_inputs({"language": "python", "source_code": "print(1)", "error_input": "a" * (settings.MAX_ERROR_CHARS + 1)})
    assert f"max {settings.MAX_ERROR_CHARS:,} characters" in exc.value.message

def test_collector_basic():
    records = classify_and_split("NameError: name 'x' is not defined")
    assert len(records) == 1
    assert records[0].original_text == "NameError: name 'x' is not defined"

def test_preprocessor_text_hygiene():
    # BOM, ANSI, tabs, trailing noise
    raw = "\ufeff\x1B[31mprint('hello')\x1B[0m\t \r\n  "
    cleaned = clean_text(raw)
    assert cleaned == "print('hello')\n"

def test_preprocessor_preserves_line_numbers():
    raw_source = "line1\r\n\tline2 \nline3"
    records = classify_and_split("error")
    norm = preprocess(Language.PYTHON, raw_source, records, None)
    
    # original had 3 lines
    lines = norm.source_code.split('\n')
    assert len(lines) == 3
    assert lines[0] == "line1"
    assert lines[1] == "    line2" # tab replaced with 4 spaces, trailing space stripped
    assert lines[2] == "line3"

def test_preprocessor_secret_redaction():
    raw_source = 'API_KEY = "sk-12345"\npassword: "mysecretpassword"'
    records = classify_and_split("token=abcdef")
    
    norm = preprocess(Language.PYTHON, raw_source, records, None)
    redacted = create_redacted_copy(norm)
    
    assert "sk-12345" not in redacted.source_code
    assert "API_KEY = <REDACTED>" in redacted.source_code
    assert "password: <REDACTED>" in redacted.source_code
    
    assert "abcdef" not in redacted.error_text_clean
    assert "token= <REDACTED>" in redacted.error_text_clean
    
    assert redacted.redaction_report.redacted_items == 5

def test_language_registry():
    class DummyAnalyzer:
        def analyze(self, x): return []
        
    register_analyzer(Language.PYTHON, DummyAnalyzer())
    analyzer = get_analyzer(Language.PYTHON)
    assert isinstance(analyzer, DummyAnalyzer)
    assert "python" in get_supported_languages()
    
    with pytest.raises(ValueError):
        get_analyzer(Language.JAVA)
