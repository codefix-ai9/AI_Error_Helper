import pytest
from unittest.mock import patch, MagicMock
from backend.app.models.requests import AnalyzeRequest
from backend.app.models.responses import AnalysisResult
from backend.app.models.stages import Location, Finding, AIOutcome, StaticAnalysisResult, NormalizedInput, AIRequestContext
from backend.app.models.enums import ErrorType, EvidenceLevel, Severity, AIStatus
from backend.app.application.services import AnalysisService

@pytest.fixture
def service():
    mock_ai_engine = MagicMock()
    mock_history = MagicMock()
    return AnalysisService(ai_engine=mock_ai_engine, history=mock_history)

def test_pipeline_success(service):
    # Setup mock AI engine to return a successful outcome
    service.ai_engine.explain.return_value = AIOutcome(status=AIStatus.OK, suggestions=[])
    
    req = AnalyzeRequest(source_code="print('Hello'\n", error_input="SyntaxError: unexpected EOF", language="python")
    result = service.analyze(req)
    
    assert isinstance(result, AnalysisResult)
    assert result.error_type == ErrorType.SYNTAX.value
    assert result.severity == Severity.HIGH.value
    assert "static" in result.confidence_basis

def test_dedup_by_category_and_input_source(service):
    # Mock parsers to return multiple findings of same category from same input source (error_text)
    service.ai_engine.explain.return_value = AIOutcome(status=AIStatus.OK)
    
    req = AnalyzeRequest(source_code="x = 1", error_input="NameError: name 'foo' is not defined", language="python")
    with patch('backend.app.application.services.parse_traceback') as mock_tb, \
         patch.object(service.rule_engine, 'evaluate') as mock_re:
        
        mock_tb.return_value = (Finding(rule_id="TB1", category="Name / Reference", evidence_level=EvidenceLevel.PATTERN, source="traceback_parser", message="NameError", location=Location()), [])
        mock_re.return_value = (Finding(rule_id="RE1", category="Name / Reference", evidence_level=EvidenceLevel.PATTERN, source="rule_engine", message="NameError", location=Location()), [])
        
        result = service.analyze(req)
        
        # Should not be corroborated because it's from the same underlying input
        assert result.confidence == 0.70 # PATTERN level without corroboration modifier

def test_primary_finding_selection(service):
    service.ai_engine.explain.return_value = AIOutcome(status=AIStatus.OK)
    req = AnalyzeRequest(source_code="def foo(x=[]): pass", error_input="Traceback...\nTypeError: foo() missing 1 required positional argument", language="python")
    
    with patch('backend.app.application.services.parse_traceback') as mock_tb, \
         patch.object(service.rule_engine, 'evaluate') as mock_re:
        
        # Traceback gives a TYPE (HIGH severity, PATTERN)
        mock_tb.return_value = (Finding(rule_id="TB1", category="Type", evidence_level=EvidenceLevel.PATTERN, source="traceback_parser", message="TypeError", location=Location()), [])
        
        # Rule engine gives LOGIC (MEDIUM severity, PATTERN) - mutable default
        mock_re.return_value = (Finding(rule_id="PY_LOGIC_MUTABLE_DEFAULT", category="Logic", evidence_level=EvidenceLevel.PATTERN, source="rule_engine", message="def foo(x=[]):", location=Location()), [])
        
        result = service.analyze(req)
        
        # Primary should be Type because HIGH > MEDIUM
        assert result.error_type == "Type"
        assert result.severity == "HIGH"

def test_authority_lock(service):
    # AI Engine tries to return a totally different error_type
    service.ai_engine.explain.return_value = AIOutcome(
        status=AIStatus.OK,
        payload={"error_type": "Configuration", "severity": "LOW", "location": {"line": 99}}
    )
    
    req = AnalyzeRequest(source_code="print('Hello'\n", error_input="SyntaxError: unexpected EOF", language="python")
    result = service.analyze(req)
    
    # Assert orchestrator enforced authority lock
    assert result.error_type == ErrorType.SYNTAX.value
    assert result.severity == Severity.HIGH.value
    assert result.location.line == 1

def test_pipeline_exception_handling(service):
    # Force a failure in validation or anywhere else
    with patch('backend.app.application.services.validate_analyze_request', side_effect=Exception("Critical system failure")):
        req = AnalyzeRequest(source_code="valid", error_input="valid", language="python")
        result = service.analyze(req)
        
        # Must not crash, must return valid AnalysisResult
        assert result.error_type == ErrorType.UNKNOWN.value
        assert "Critical system failure" in result.analysis_metadata.analyzer_errors[0]
