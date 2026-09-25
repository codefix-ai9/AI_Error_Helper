import pytest
from backend.app.models.enums import Language
from backend.app.collector.collector import classify_and_split
from backend.app.preprocessing.preprocessor import preprocess, create_redacted_copy

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
