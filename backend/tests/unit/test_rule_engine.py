import pytest
import time
from unittest.mock import patch
from backend.app.models.stages import Location
from backend.app.models.enums import EvidenceLevel
from backend.app.analysis.rules.engine import RuleEngine, compute_confidence, load_rules

def test_compute_confidence():
    assert compute_confidence(EvidenceLevel.CONFIRMED, corroborated=False, conflict=False) == 0.90
    assert compute_confidence(EvidenceLevel.PATTERN, corroborated=False, conflict=False) == 0.70
    assert compute_confidence(EvidenceLevel.HEURISTIC, corroborated=False, conflict=False) == 0.40
    assert compute_confidence(EvidenceLevel.NONE, corroborated=False, conflict=False) is None
    
    assert compute_confidence(EvidenceLevel.CONFIRMED, corroborated=True, conflict=False) == 0.95
    assert compute_confidence(EvidenceLevel.CONFIRMED, corroborated=True, conflict=True) == 0.80
    assert round(compute_confidence(EvidenceLevel.HEURISTIC, corroborated=False, conflict=True), 2) == 0.25
    assert compute_confidence(EvidenceLevel.CONFIRMED, corroborated=True, conflict=False) <= 0.95

def test_engine_match_basic():
    engine = RuleEngine([
        {
            "id": "PY_TEST_001",
            "error_type": "Name / Reference",
            "pattern": r"^NameError: name '(.+)' is not defined$",
            "evidence_level": "PATTERN",
            "match_target": "error_text"
        }
    ])
    finding, errors = engine.evaluate("NameError: name 'foo' is not defined")
    assert finding is not None
    assert len(errors) == 0
    assert finding.rule_id == "PY_TEST_001"

def test_engine_no_match():
    engine = RuleEngine([
        {
            "id": "PY_TEST_001",
            "error_type": "Name / Reference",
            "pattern": r"^NameError: name '(.+)' is not defined$",
            "evidence_level": "PATTERN"
        }
    ])
    finding, errors = engine.evaluate("ValueError: something else")
    assert finding is None
    assert len(errors) == 0

def test_engine_exception_caught():
    engine = RuleEngine([
        {
            "id": "PY_TEST_001",
            "error_type": "Name / Reference",
            "pattern": r"^NameError: name '(.+)' is not defined$",
            "evidence_level": "PATTERN"
        }
    ])
    
    class MockPattern:
        def search(self, text):
            raise Exception("Regex engine failed")
            
    engine.compiled_rules[0] = (engine.rules[0], MockPattern())
    finding, errors = engine.evaluate("NameError: name 'foo' is not defined")
    assert finding is None
    assert len(errors) == 1
    assert "Regex engine failed" in errors[0]

def test_timing_regression_python_rules():
    rules = load_rules('python')
    engine = RuleEngine(rules)
    adversarial_inputs = [
        "A" * 20000,
        ("NameError: " + "A" * 100 + " ") * 100,
        ("File " + "a" * 100 + " line 10\n") * 100,
        ("def f(x=" + "[" * 1000 + "]" * 1000 + "):\n") * 10,
        ("== None" * 2000)
    ]
    for adv_input in adversarial_inputs:
        start = time.time()
        finding, errors = engine.evaluate(error_text=adv_input, source_code=adv_input)
        duration = time.time() - start
        assert duration < 0.1, f"Regex evaluation took too long: {duration}s"
        assert len(errors) == 0

def test_logic_mutable_default():
    engine = RuleEngine(load_rules('python'))
    source = "def foo(x=[]):\n    pass\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_MUTABLE_DEFAULT"
    assert finding.location.line == 1

def test_logic_bare_except():
    engine = RuleEngine(load_rules('python'))
    source = "try:\n    pass\nexcept:\n    pass\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_BARE_EXCEPT"
    assert finding.location.line == 3

def test_logic_eq_none():
    engine = RuleEngine(load_rules('python'))
    source = "if x == None:\n    print(1)\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_EQ_NONE"
    assert finding.location.line == 1

def test_logic_float_eq():
    engine = RuleEngine(load_rules('python'))
    source = "val = 3.14\nif val == 3.14:\n    pass\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_FLOAT_EQ"
    assert finding.location.line == 2

def test_logic_is_literal():
    engine = RuleEngine(load_rules('python'))
    source = "if x is 'hello':\n    pass\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_IS_LITERAL"
    assert finding.location.line == 1
    
    source_num = "if x is 5:\n    pass\n"
    finding2, _ = engine.evaluate(error_text="", source_code=source_num)
    assert finding2 is not None
    assert finding2.rule_id == "PY_LOGIC_IS_LITERAL"

def test_logic_builtin_shadow():
    engine = RuleEngine(load_rules('python'))
    source = "def foo():\n    list = [1, 2]\n"
    finding, _ = engine.evaluate(error_text="", source_code=source)
    assert finding is not None
    assert finding.rule_id == "PY_LOGIC_BUILTIN_SHADOW"
    assert finding.location.line == 2
