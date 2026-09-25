import ast
from typing import Optional, Tuple, List
from backend.app.models.stages import Finding, Location
from backend.app.models.enums import ErrorType, EvidenceLevel

def parse_ast_for_errors(source_code: str) -> Tuple[Optional[Finding], List[str]]:
    analyzer_errors = []
    try:
        ast.parse(source_code)
        return None, analyzer_errors
    except SyntaxError as e:
        category = ErrorType.SYNTAX.value
        if "indent" in str(e).lower():
            category = ErrorType.INDENTATION.value
            
        return Finding(
            rule_id="PY_SYNTAX_001",
            category=category,
            evidence_level=EvidenceLevel.CONFIRMED,
            source="ast_parser",
            message=str(e),
            location=Location(line=e.lineno, column=e.offset)
        ), analyzer_errors
    except Exception as e:
        analyzer_errors.append(f"ast_parser internal error: {type(e).__name__}: {str(e)}")
        return None, analyzer_errors
