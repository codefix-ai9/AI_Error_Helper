import pytest
from unittest.mock import patch
from backend.app.models.stages import Location
from backend.app.analysis.languages.python.ast_parser import parse_ast_for_errors
from backend.app.analysis.languages.python.traceback_parser import parse_traceback

def test_ast_parser_valid_code():
    source = "print('Hello, World!')\nx = 1\n"
    finding, errors = parse_ast_for_errors(source)
    assert finding is None
    assert len(errors) == 0

def test_ast_parser_syntax_error():
    source = "print('Hello, World!'\nx = 1\n" # Missing closing paren
    finding, errors = parse_ast_for_errors(source)
    assert finding is not None
    assert finding.category == "Syntax"
    assert finding.message.startswith("unexpected EOF while parsing") or "unterminated string" in finding.message or "invalid syntax" in finding.message or "(" in finding.message
    assert finding.location.line == 1 or finding.location.line == 2
    assert len(errors) == 0

def test_ast_parser_indentation_error():
    source = "def foo():\nprint('bar')\n"
    finding, errors = parse_ast_for_errors(source)
    assert finding is not None
    assert finding.category == "Indentation"
    assert "expected an indented block" in finding.message
    assert finding.location.line == 2
    assert len(errors) == 0

def test_traceback_parser_standard():
    tb_text = """Traceback (most recent call last):
  File "example.py", line 4, in <module>
    foo()
  File "example.py", line 2, in foo
    print(1 / 0)
ZeroDivisionError: division by zero"""
    
    finding, errors = parse_traceback(tb_text)
    assert finding is not None
    assert finding.category == "Runtime"
    assert finding.message == "ZeroDivisionError: division by zero"
    assert finding.location.line == 2
    assert len(errors) == 0

def test_traceback_parser_no_traceback():
    tb_text = "Just some random error text without traceback"
    finding, errors = parse_traceback(tb_text)
    assert finding is None
    assert len(errors) == 0

def test_traceback_parser_name_error():
    tb_text = """Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'bar' is not defined"""
    finding, errors = parse_traceback(tb_text)
    assert finding is not None
    assert finding.category == "Name / Reference"
    assert finding.message == "NameError: name 'bar' is not defined"
    assert finding.location.line == 1
    assert len(errors) == 0

def test_ast_parser_deeply_nested_code():
    source = "[" * 1500 + "1" + "]" * 1500
    with patch('backend.app.analysis.languages.python.ast_parser.ast.parse', side_effect=RecursionError("maximum recursion depth exceeded during compilation")):
        finding, errors = parse_ast_for_errors(source)
    assert finding is None
    assert len(errors) == 1
    assert "RecursionError" in errors[0]

def test_traceback_parser_multi_frame():
    tb_text = """Traceback (most recent call last):
  File "main.py", line 10, in <module>
    call_a()
  File "a.py", line 5, in call_a
    call_b()
  File "b.py", line 42, in call_b
    raise ValueError("Deep error")
ValueError: Deep error"""
    finding, errors = parse_traceback(tb_text)
    assert len(errors) == 0
    assert finding is not None
    assert finding.location.line == 42
    assert finding.category == "Type"
    assert finding.message == "ValueError: Deep error"

def test_traceback_parser_internal_failure():
    with patch('backend.app.analysis.languages.python.traceback_parser.re.finditer', side_effect=Exception("Mocked internal failure")):
        finding, errors = parse_traceback("Traceback (most recent call last):\n  File \"a.py\", line 1\nError")
        assert finding is None
        assert len(errors) == 1
        assert "Mocked internal failure" in errors[0]
        assert "traceback_parser internal error" in errors[0]
