import pytest
from backend.app.models.enums import Language
from backend.app.collector.collector import classify_and_split
from backend.app.preprocessing.preprocessor import preprocess, clean_text
from backend.app.analysis.registry import register_analyzer, get_analyzer, get_supported_languages

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

def test_language_registry():
    class DummyAnalyzer:
        def analyze(self, x): return []
        
    register_analyzer(Language.PYTHON, DummyAnalyzer())
    analyzer = get_analyzer(Language.PYTHON)
    assert isinstance(analyzer, DummyAnalyzer)
    assert "python" in get_supported_languages()
    
    # Graceful degradation fallback
    fallback = get_analyzer(Language.JAVA)
    assert type(fallback).__name__ == "FallbackAnalyzer"
    assert fallback.analyze(None) == []
