import re
from backend.app.models.stages import NormalizedInput, RedactionReport, ErrorRecord
from backend.app.models.enums import Language
from typing import List, Optional

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
SECRET_PATTERN = re.compile(r'(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?')

def clean_text(text: str) -> str:
    if not text:
        return text
    # Strip BOM
    if text.startswith('\ufeff'):
        text = text[1:]
    # Remove ANSI codes
    text = ANSI_ESCAPE.sub('', text)
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace tabs with 4 spaces (preserves line numbers)
    text = text.replace('\t', '    ')
    # Right-strip trailing spaces
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text

def redact_text(text: str, report: RedactionReport) -> str:
    if not text:
        return text
    
    def repl(match):
        report.redacted_items += 1
        if "secret_pattern" not in report.patterns_used:
            report.patterns_used.append("secret_pattern")
        matched_str = match.group(0)
        # We'll just replace the value with REDACTED
        idx = matched_str.find('=')
        if idx == -1:
            idx = matched_str.find(':')
        if idx != -1:
            return matched_str[:idx+1] + " <REDACTED>"
        return "<REDACTED>"

    return SECRET_PATTERN.sub(repl, text)

def preprocess(language: Language, source_code: str, error_records: List[ErrorRecord], expected_behavior: Optional[str]) -> NormalizedInput:
    clean_src = clean_text(source_code)
    clean_records = []
    
    for r in error_records:
        cr = ErrorRecord(
            original_text=clean_text(r.original_text),
            error_type=r.error_type,
            message=clean_text(r.message) if r.message else None,
            frame_location=r.frame_location
        )
        clean_records.append(cr)
        
    error_text_clean = "\n".join(r.original_text for r in clean_records)
    
    return NormalizedInput(
        language=language,
        source_code=clean_src,
        error_records=clean_records,
        error_text_clean=error_text_clean,
        redaction_report=RedactionReport(),
        expected_behavior=clean_text(expected_behavior) if expected_behavior else None
    )

def create_redacted_copy(normalized: NormalizedInput) -> NormalizedInput:
    report = RedactionReport()
    redacted_src = redact_text(normalized.source_code, report)
    redacted_err = redact_text(normalized.error_text_clean, report)
    
    redacted_records = []
    for r in normalized.error_records:
        redacted_records.append(ErrorRecord(
            original_text=redact_text(r.original_text, report),
            error_type=r.error_type,
            message=redact_text(r.message, report) if r.message else None,
            frame_location=r.frame_location
        ))
        
    return NormalizedInput(
        language=normalized.language,
        source_code=redacted_src,
        error_records=redacted_records,
        error_text_clean=redacted_err,
        redaction_report=report,
        expected_behavior=redact_text(normalized.expected_behavior, report) if normalized.expected_behavior else None
    )
