import difflib
import ast
from typing import Optional
from backend.app.models.stages import CorrectionDiff, Finding
from backend.app.models.enums import ErrorType

def verify_correction(corrected_code: str) -> bool:
    """Verifies that the corrected code is syntactically valid by attempting to parse it."""
    try:
        ast.parse(corrected_code)
        return True
    except SyntaxError:
        return False

def generate_correction_diff(original: str, corrected: str) -> CorrectionDiff:
    """Generates a correction diff using difflib."""
    original_lines = original.splitlines()
    corrected_lines = corrected.splitlines()

    unified_diff = list(difflib.unified_diff(
        original_lines, corrected_lines, 
        fromfile='original', tofile='corrected', lineterm=''
    ))
    
    changed_lines_before = []
    changed_lines_after = []
    
    if unified_diff:
        for i, line in enumerate(unified_diff):
            if line.startswith('@@'):
                parts = line.split(' ')
                if len(parts) >= 3:
                    try:
                        before_start = int(parts[1].split(',')[0].replace('-', ''))
                        after_start = int(parts[2].split(',')[0].replace('+', ''))
                        changed_lines_before.append(before_start)
                        changed_lines_after.append(after_start)
                    except ValueError:
                        pass
                        
    return CorrectionDiff(
        changed_lines_before=changed_lines_before,
        changed_lines_after=changed_lines_after,
        unified="\n".join(unified_diff)
    )

def attempt_deterministic_correction(source_code: str, finding: Finding) -> Optional[str]:
    """Attempts to generate a corrected version of the source code for simple, deterministic errors."""
    if finding.category == ErrorType.SYNTAX.value and finding.location and finding.location.line:
        lines = source_code.splitlines()
        line_idx = finding.location.line - 1
        if 0 <= line_idx < len(lines):
            line = lines[line_idx]
            msg = finding.message.lower()
            
            # Heuristic for missing colon
            if "expected ':'" in msg or "invalid syntax" in msg:
                # If it's a def, class, if, elif, else, for, while, try, except, finally, with
                # and it doesn't end with a colon
                stripped = line.rstrip()
                if stripped and not stripped.endswith(':'):
                    # Check if it looks like a block starter
                    keywords = ('def ', 'class ', 'if ', 'elif ', 'else', 'for ', 'while ', 'try', 'except', 'finally', 'with ')
                    if any(stripped.lstrip().startswith(kw) for kw in keywords):
                        # Attempt to add a colon
                        lines[line_idx] = stripped + ':'
                        return "\n".join(lines)
    return None
