import pytest
from backend.app.application.services import AnalysisService
from backend.app.ai.engine import build_ai_engine
from backend.app.core.config import settings
from backend.app.models.requests import AnalyzeRequest
from backend.app.models.enums import Language, ErrorType

class DummyHistory:
    def save(self, res): return True

@pytest.fixture
def service():
    return AnalysisService(ai_engine=build_ai_engine(settings), history=DummyHistory())

def test_sample_case_1_syntax_error(service):
    req = AnalyzeRequest(
        language=Language.PYTHON,
        source_code="print('Hello World'\n",
        error_input="SyntaxError: unexpected EOF while parsing"
    )
    res = service.analyze(req)
    assert res.error_type == ErrorType.SYNTAX.value
    assert res.severity == "HIGH"
    
def test_sample_case_2_name_error(service):
    req = AnalyzeRequest(
        language=Language.PYTHON,
        source_code="def calc():\n    return x + 1",
        error_input='Traceback (most recent call last):\n  File "test.py", line 2, in calc\nNameError: name \'x\' is not defined'
    )
    res = service.analyze(req)
    assert res.error_type == ErrorType.NAME_REFERENCE.value
    assert res.severity == "HIGH"

def test_sample_case_3_logic_mutable_default(service):
    req = AnalyzeRequest(
        language=Language.PYTHON,
        source_code="def add_item(item, lst=[]):\n    lst.append(item)\n    return lst",
        error_input="Why does lst keep growing between calls?"
    )
    res = service.analyze(req)
    assert res.error_type == ErrorType.LOGIC.value
    assert res.severity == "MEDIUM"

def test_sample_case_4_type_error(service):
    req = AnalyzeRequest(
        language=Language.PYTHON,
        source_code="print('Number: ' + 5)",
        error_input="Traceback (most recent call last):\n  File \"script.py\", line 1, in <module>\nTypeError: can only concatenate str (not \"int\") to str"
    )
    res = service.analyze(req)
    assert res.error_type == ErrorType.TYPE.value
    assert res.severity == "HIGH"

def test_sample_case_5_java_graceful_degrade(service):
    # Java gracefully degrades
    req = AnalyzeRequest(
        language=Language.JAVA,
        source_code="public class Main { public static void main(String[] args) {} }",
        error_input="Some Error"
    )
    res = service.analyze(req)
    assert res.error_type == ErrorType.UNKNOWN.value
    assert "java" not in res.analysis_metadata.analyzers_run
