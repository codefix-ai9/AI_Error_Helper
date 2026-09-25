import re
from typing import Optional, Tuple, List
from backend.app.models.stages import Finding, Location
from backend.app.models.enums import ErrorType, EvidenceLevel

def parse_traceback(tb_text: str) -> Tuple[Optional[Finding], List[str]]:
    analyzer_errors = []
    try:
        # Look for the last file/line mention
        file_pattern = r'File "([^"]+)", line (\d+)'
        matches = list(re.finditer(file_pattern, tb_text))
        
        if not matches:
            return None, analyzer_errors
            
        last_match = matches[-1]
        line_number = int(last_match.group(2))
        
        # Extract the error message (last line of traceback)
        lines = tb_text.strip().split('\n')
        error_message = lines[-1].strip()
        
        # Map common Python exceptions to categories
        category = ErrorType.RUNTIME.value
        if error_message.startswith("NameError") or error_message.startswith("UnboundLocalError"):
            category = ErrorType.NAME_REFERENCE.value
        elif error_message.startswith("TypeError") or error_message.startswith("ValueError"):
            category = ErrorType.TYPE.value
        elif error_message.startswith("ImportError") or error_message.startswith("ModuleNotFoundError"):
            category = ErrorType.IMPORT.value
        elif error_message.startswith("SyntaxError"):
            category = ErrorType.SYNTAX.value
        elif error_message.startswith("IndentationError"):
            category = ErrorType.INDENTATION.value
            
        return Finding(
            rule_id="PY_TB_001",
            category=category,
            evidence_level=EvidenceLevel.PATTERN,
            source="traceback_parser",
            message=error_message,
            location=Location(line=line_number)
        ), analyzer_errors
    except Exception as e:
        analyzer_errors.append(f"traceback_parser internal error: {type(e).__name__}: {str(e)}")
        return None, analyzer_errors
