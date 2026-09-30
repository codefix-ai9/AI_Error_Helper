"""
MockProvider — deterministic canned responses per ErrorType (§7.1).

Always returns valid JSON matching the AIExplanation schema.
Used when LLM_PROVIDER=mock and in all tests.
"""
import json
from typing import Any, Dict

_CANNED: Dict[str, dict] = {
    "Syntax": {
        "explanation": (
            "Your code has a syntax error, which means Python cannot parse it at all. "
            "This is like a grammar mistake — the interpreter stops before running anything."
        ),
        "probable_cause": "A missing colon, bracket, or incorrect indentation is preventing the file from being parsed.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Read the error message: it tells you the exact line number.",
            "Look at the line and the line before it for missing colons or brackets.",
            "Check that your indentation uses only spaces (not mixed tabs and spaces).",
            "Run the file after fixing the issue to confirm the error is resolved.",
        ],
        "prevention_tip": "Use a code editor with syntax highlighting to catch mistakes as you type.",
        "key_concept": "Python syntax rules",
        "uncertainty_note": "The exact fix depends on the specific syntax error in your code.",
        "suggested_category": None,
    },
    "Runtime": {
        "explanation": (
            "Your code runs but crashes while executing. Runtime errors happen when Python "
            "encounters an operation it cannot complete, such as dividing by zero or accessing "
            "a list index that doesn't exist."
        ),
        "probable_cause": "An operation failed at runtime — check the traceback for the exact line.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Read the traceback from bottom to top — the last line shows the error type.",
            "Find the line number in your own file (ignore library frames).",
            "Add a print statement before that line to inspect the values of variables.",
            "Think about edge cases: what if a list is empty, or a value is zero?",
            "Fix the root cause and re-run.",
        ],
        "prevention_tip": "Validate inputs and use try/except to handle expected failure modes gracefully.",
        "key_concept": "Runtime exception handling",
        "uncertainty_note": "Without seeing the full runtime state, the exact cause is inferred from the traceback.",
        "suggested_category": None,
    },
    "Type": {
        "explanation": (
            "Python encountered a type mismatch. For example, you may have tried to add "
            "a string and a number, or passed the wrong kind of argument to a function."
        ),
        "probable_cause": "A variable holds a different type than expected by the operation or function.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Check the error message — it usually says 'expected X, got Y'.",
            "Print type(variable) for each variable involved in the failing expression.",
            "Trace where the variable was created and what type it was assigned.",
            "Convert the value to the correct type before using it.",
        ],
        "prevention_tip": "Use type hints and run a type checker like mypy to catch type errors before running your code.",
        "key_concept": "Python dynamic typing and type conversion",
        "uncertainty_note": "The exact types involved depend on runtime values.",
        "suggested_category": None,
    },
    "Name / Reference": {
        "explanation": (
            "Python tried to use a name (variable or function) that hasn't been defined. "
            "This is a NameError — the name is referenced before it is assigned a value."
        ),
        "probable_cause": "The variable or function is either misspelled, used before assignment, or defined in a different scope.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Check the exact spelling of the name — Python is case-sensitive.",
            "Look for where the variable is defined and make sure it runs before this line.",
            "If it is inside a function, it will not be visible outside (scope rules).",
            "Define the variable before you use it.",
        ],
        "prevention_tip": "Define all variables at the top of the function or module before using them.",
        "key_concept": "Variable scope and NameError",
        "uncertainty_note": "If the name is conditionally defined (inside an if block), it may be missing at runtime.",
        "suggested_category": None,
    },
    "Import": {
        "explanation": (
            "Python could not find the module you are trying to import. "
            "This could be a spelling mistake, a wrong path, or a missing installation."
        ),
        "probable_cause": "The module name is misspelled, the file is in the wrong location, or the import path is incorrect.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Check the spelling of the module name.",
            "Make sure the file you are importing is in the same directory or on the Python path.",
            "If importing from a package, check that __init__.py exists.",
            "Try importing in the Python shell to isolate the problem.",
        ],
        "prevention_tip": "Use explicit relative or absolute imports and organize your project with a clear structure.",
        "key_concept": "Python import system and module search path",
        "uncertainty_note": "The exact cause depends on your project structure.",
        "suggested_category": None,
    },
    "Dependency": {
        "explanation": (
            "A required third-party package is not installed in your Python environment. "
            "You must install it before running your code."
        ),
        "probable_cause": "The package was not installed, or you are using the wrong Python environment.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Run: pip install <package-name> in your terminal.",
            "Check that you are using the correct Python environment (virtualenv, conda, etc.).",
            "If you have a requirements.txt, run: pip install -r requirements.txt.",
            "Verify the installation with: pip show <package-name>.",
        ],
        "prevention_tip": "Always use a virtual environment and keep a requirements.txt file up to date.",
        "key_concept": "Python package management and virtual environments",
        "uncertainty_note": "Package name and version requirements are inferred from the error message.",
        "suggested_category": None,
    },
    "Indentation": {
        "explanation": (
            "Python uses indentation to define code blocks. An IndentationError means "
            "a line is indented at the wrong level or uses a mix of tabs and spaces."
        ),
        "probable_cause": "Inconsistent use of tabs and spaces, or a line indented at the wrong level.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Look at the line number in the error and inspect its indentation.",
            "Make sure you use ONLY spaces (4 per level is standard) or ONLY tabs — not both.",
            "Check that all lines inside a block (if, for, def, etc.) are indented equally.",
            "Use your editor's 'Show whitespace' feature to spot mixed indentation.",
        ],
        "prevention_tip": "Configure your editor to convert tabs to 4 spaces automatically.",
        "key_concept": "Python indentation and code blocks",
        "uncertainty_note": "The exact line may vary; check the full indentation of your file.",
        "suggested_category": None,
    },
    "Logic": {
        "explanation": (
            "Your code runs without error, but produces incorrect output. "
            "This is a logic error — the algorithm or conditions do not match the intended behaviour."
        ),
        "probable_cause": "A condition, operator, or algorithm step is incorrect.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Add print statements to trace the values of key variables at each step.",
            "Walk through the code manually with a simple test case on paper.",
            "Check boundary conditions: what happens with empty input, zero, or the largest value?",
            "Compare your logic to the problem specification step by step.",
            "Use a debugger to step through the code line by line.",
        ],
        "prevention_tip": "Write small test cases for each function before combining them.",
        "key_concept": "Debugging logic errors and test-driven thinking",
        "uncertainty_note": "Logic errors are inferred from patterns in the code; the exact bug requires running the code with specific inputs.",
        "suggested_category": None,
    },
    "Configuration": {
        "explanation": (
            "Your program is failing because of a configuration issue — "
            "a required environment variable, file, or setting is missing or incorrect."
        ),
        "probable_cause": "A configuration value is missing, has the wrong format, or points to a non-existent resource.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Read the error message carefully — it usually names the missing config key or file.",
            "Check your .env file or config file for the expected key.",
            "Verify the value is correct (path exists, format matches expected type).",
            "Compare with the example config file if one is provided.",
        ],
        "prevention_tip": "Always provide an .env.example with all required keys documented.",
        "key_concept": "Configuration management and environment variables",
        "uncertainty_note": "The exact configuration required depends on your application setup.",
        "suggested_category": None,
    },
    "Unknown / Requires Review": {
        "explanation": (
            "The error could not be confidently classified by static analysis. "
            "The suggestions below are based on patterns in your code and error message, "
            "but manual review is recommended."
        ),
        "probable_cause": "The error does not match a known pattern — review the full stack trace and code logic.",
        "affected_code": None,
        "corrected_code": None,
        "debugging_steps": [
            "Read the full error message and traceback carefully.",
            "Search for the error message text in your language's documentation.",
            "Isolate the smallest code snippet that reproduces the error.",
            "Ask a peer or post to a forum with the minimal example.",
        ],
        "prevention_tip": "When stuck, isolate the problem to the smallest reproducible case.",
        "key_concept": "Systematic debugging",
        "uncertainty_note": "This is a best-effort explanation — the error type is unconfirmed.",
        "suggested_category": None,
    },
}

_DEFAULT_CANNED = _CANNED["Unknown / Requires Review"]


class MockProvider:
    """
    Deterministic mock provider. Returns canned output per ErrorType.
    Never calls any external service.
    """

    def generate_structured(
        self,
        system_prompt: str,
        payload: Dict[str, Any],
        json_schema: Dict[str, Any],
    ) -> str:
        error_type = payload.get("detected_category", "Unknown / Requires Review")
        canned = _CANNED.get(error_type, _DEFAULT_CANNED).copy()

        # If source code is provided, try to use a real snippet for affected_code
        source = payload.get("source_code", "")
        if source:
            # Use first non-empty line of source as affected_code placeholder
            for line in source.splitlines():
                if line.strip():
                    canned = dict(canned)
                    canned["affected_code"] = None  # keep null — safe default
                    break

        return json.dumps(canned)
