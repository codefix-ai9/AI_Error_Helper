import pytest
from backend.app.models.stages import CorrectionDiff, Finding, Location
from backend.app.models.enums import ErrorType, EvidenceLevel
from backend.app.analysis.recommendation import generate_correction_diff, verify_correction, attempt_deterministic_correction


def test_generate_correction_diff():
    original = "def foo()\n    pass"
    corrected = "def foo():\n    pass"
    
    diff = generate_correction_diff(original, corrected)
    assert diff is not None
    assert diff.changed_lines_before == [1]
    assert diff.changed_lines_after == [1]
    assert "def foo():" in diff.unified

def test_verify_correction_valid():
    corrected = "def foo():\n    pass"
    assert verify_correction(corrected) is True

def test_verify_correction_invalid():
    corrected = "def foo()  # still invalid\n    pass"
    assert verify_correction(corrected) is False

def test_attempt_deterministic_correction():
    source_code = "def foo()\n    pass"
    finding = Finding(
        rule_id="PY_SYNTAX_001",
        category=ErrorType.SYNTAX.value,
        evidence_level=EvidenceLevel.CONFIRMED,
        source="ast_parser",
        message="SyntaxError: expected ':'",
        location=Location(line=1, column=9)
    )
    
    corrected = attempt_deterministic_correction(source_code, finding)
    assert corrected is not None
    assert corrected == "def foo():\n    pass"

def test_attempt_deterministic_correction_no_match():
    source_code = "def foo():\n    pasx"
    finding = Finding(
        rule_id="PY_SYNTAX_001",
        category=ErrorType.SYNTAX.value,
        evidence_level=EvidenceLevel.CONFIRMED,
        source="ast_parser",
        message="SyntaxError: unexpected EOF",
        location=Location(line=2, column=4)
    )
    
    corrected = attempt_deterministic_correction(source_code, finding)
    assert corrected is None

