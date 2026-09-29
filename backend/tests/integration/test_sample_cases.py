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
    assert res.error_type == ErrorType.UNKNOWN.value
    assert "java" not in res.analysis_metadata.analyzers_run


# IMPORT ERRORS (3 cases)

# IMPORT ERRORS (3 cases)

# IMPORT ERRORS (3 cases)
def test_sample_case_6_import_module_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import django', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nModuleNotFoundError: No module named \'django\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_7_import_cannot_import_name(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='from math import random_func', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: cannot import name \'random_func\' from \'math\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_8_import_circular_dependency(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import a', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: cannot import name \'x\' from partially initialized module \'a\' (most likely due to a circular import)')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

# CONFIGURATION ERRORS (3 cases)
def test_sample_case_9_config_missing_env(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import os\nDB = os.environ[\'DB_HOST\']', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\nKeyError: \'DB_HOST\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_10_config_file_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='open(\'config.json\')', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nFileNotFoundError: [Errno 2] No such file or directory: \'config.json\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_11_config_invalid_json(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import json\njson.loads(\'bad\')', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

# DEPENDENCY ERRORS (4 cases)
def test_sample_case_12_dependency_version_conflict(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import pkg_resources', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\npkg_resources.VersionConflict: (requests 2.20.0, Requirement.parse(\'requests>=2.25.0\'))')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_13_dependency_missing_so(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import cv2', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: libGL.so.1: cannot open shared object file: No such file or directory')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_14_dependency_attribute_missing(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import requests\nrequests.non_existent_feature()', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\nAttributeError: module \'requests\' has no attribute \'non_existent_feature\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_15_dependency_distribution_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import pkg_resources', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\npkg_resources.DistributionNotFound: The \'pydantic\' distribution was not found')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

# IMPORT ERRORS (3 cases)
def test_sample_case_6_import_module_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import django', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nModuleNotFoundError: No module named \'django\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_7_import_cannot_import_name(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='from math import random_func', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: cannot import name \'random_func\' from \'math\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_8_import_circular_dependency(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import a', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: cannot import name \'x\' from partially initialized module \'a\' (most likely due to a circular import)')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

# CONFIGURATION ERRORS (3 cases)
def test_sample_case_9_config_missing_env(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import os\nDB = os.environ[\'DB_HOST\']', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\nKeyError: \'DB_HOST\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_10_config_file_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='open(\'config.json\')', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nFileNotFoundError: [Errno 2] No such file or directory: \'config.json\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_11_config_invalid_json(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import json\njson.loads(\'bad\')', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

# DEPENDENCY ERRORS (4 cases)
def test_sample_case_12_dependency_version_conflict(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import pkg_resources', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\npkg_resources.VersionConflict: (requests 2.20.0, Requirement.parse(\'requests>=2.25.0\'))')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_13_dependency_missing_so(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import cv2', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\nImportError: libGL.so.1: cannot open shared object file: No such file or directory')
    res = service.analyze(req)
    assert res.error_type == ErrorType.IMPORT.value

def test_sample_case_14_dependency_attribute_missing(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import requests\nrequests.non_existent_feature()', error_input='Traceback (most recent call last):\n  File "main.py", line 2, in <module>\nAttributeError: module \'requests\' has no attribute \'non_existent_feature\'')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value

def test_sample_case_15_dependency_distribution_not_found(service):
    req = AnalyzeRequest(language=Language.PYTHON, source_code='import pkg_resources', error_input='Traceback (most recent call last):\n  File "main.py", line 1, in <module>\npkg_resources.DistributionNotFound: The \'pydantic\' distribution was not found')
    res = service.analyze(req)
    assert res.error_type == ErrorType.RUNTIME.value
