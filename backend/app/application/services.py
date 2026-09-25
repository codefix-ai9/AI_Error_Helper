import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.models.requests import AnalyzeRequest
from backend.app.models.responses import AnalysisResult, AnalysisMetadata
from backend.app.models.stages import (
    NormalizedInput, StaticAnalysisResult, AIRequestContext, Finding, 
    AIOutcome, Location, ErrorRecord, RedactionReport, CorrectionDiff
)
from backend.app.models.enums import ErrorType, Severity, EvidenceLevel, AIStatus, Provenance

from backend.app.application.ports import AIEnginePort, HistoryPort, AnalysisServicePort
from backend.app.validation.request_validator import validate_analyze_request
from backend.app.preprocessing.preprocessor import preprocess, create_redacted_copy
from backend.app.collector.collector import classify_and_split

# Python Parsers
from backend.app.analysis.languages.python.ast_parser import parse_ast_for_errors
from backend.app.analysis.languages.python.traceback_parser import parse_traceback
from backend.app.analysis.rules.engine import RuleEngine, load_rules, compute_confidence


def get_severity(category: str) -> Severity:
    high_cats = {
        ErrorType.SYNTAX.value, 
        ErrorType.INDENTATION.value, 
        ErrorType.IMPORT.value, 
        ErrorType.DEPENDENCY.value, 
        ErrorType.NAME_REFERENCE.value, 
        ErrorType.TYPE.value, 
        ErrorType.RUNTIME.value
    }
    if category in high_cats:
        return Severity.HIGH
    if category in {ErrorType.LOGIC.value, ErrorType.CONFIGURATION.value}:
        return Severity.MEDIUM
    return Severity.UNKNOWN


def determine_input_signal(finding: Finding) -> str:
    if finding.source == 'ast_parser':
        return 'source_code'
    if finding.source == 'rule_engine' and finding.rule_id.startswith('PY_LOGIC_'):
        return 'source_code'
    return 'error_text'


class AnalysisService(AnalysisServicePort):
    def __init__(self, ai_engine: AIEnginePort, history: HistoryPort):
        self.ai_engine = ai_engine
        self.history = history
        self.python_rules = load_rules('python')
        self.rule_engine = RuleEngine(self.python_rules)

    def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
        analyzer_errors = []
        analyzers_run = []
        
        try:
            # 1. Validation
            validate_analyze_request(request.model_dump())
            
            # 2. Collector & Preprocessing
            error_records = classify_and_split(request.error_input)
            normalized = preprocess(request.language, request.source_code, error_records, request.expected_behavior)
            
            # 3. Static Analysis
            all_findings = []
            if request.language.value == 'python':
                # AST
                analyzers_run.append("python_ast_parser")
                ast_f, ast_e = parse_ast_for_errors(normalized.source_code)
                if ast_f:
                    all_findings.append(ast_f)
                analyzer_errors.extend(ast_e)
                
                # Traceback
                analyzers_run.append("python_traceback_parser")
                tb_f, tb_e = parse_traceback(normalized.error_text_clean)
                if tb_f:
                    all_findings.append(tb_f)
                analyzer_errors.extend(tb_e)
                
                # Rule Engine
                analyzers_run.append("python_rule_engine")
                re_f, re_e = self.rule_engine.evaluate(normalized.error_text_clean, normalized.source_code)
                if re_f:
                    all_findings.append(re_f)
                analyzer_errors.extend(re_e)
            else:
                # Unsupported languages (Java/JS for now just return empty)
                pass

            # 4. Dedup by (category, input_source)
            unique_findings = []
            seen = set()
            for f in all_findings:
                key = (f.category, determine_input_signal(f))
                if key not in seen:
                    seen.add(key)
                    unique_findings.append(f)
                    
            # 5. Primary Finding Selection
            primary = None
            if unique_findings:
                def sort_key(f: Finding):
                    sev_score = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}.get(get_severity(f.category).value, 0)
                    ev_score = {"CONFIRMED": 3, "PATTERN": 2, "HEURISTIC": 1, "NONE": 0}.get(f.evidence_level.value, 0)
                    line_score = -f.location.line if f.location and f.location.line else 0
                    return (sev_score, ev_score, line_score)
                    
                primary = sorted(unique_findings, key=sort_key, reverse=True)[0]
                
            # Compute corroboration & confidence
            corroborated = False
            confidence = None
            if primary:
                primary_sig = determine_input_signal(primary)
                for f in unique_findings:
                    if f != primary and f.category == primary.category and determine_input_signal(f) != primary_sig:
                        corroborated = True
                        break
                confidence = compute_confidence(primary.evidence_level, corroborated=corroborated, conflict=False)

            # Build Static Result
            static_res = StaticAnalysisResult(
                findings=unique_findings,
                primary_finding=primary,
                error_type=ErrorType(primary.category) if primary else ErrorType.UNKNOWN,
                severity=get_severity(primary.category) if primary else Severity.UNKNOWN,
                location=primary.location if primary else None,
                evidence_level=primary.evidence_level if primary else EvidenceLevel.NONE,
                corroborated=corroborated,
                analyzers_run=analyzers_run,
                analyzer_errors=analyzer_errors
            )

            # 6. AI Engine Call
            redacted_input = create_redacted_copy(normalized)
            ctx = AIRequestContext(static_result=static_res, normalized_input=redacted_input)
            ai_outcome = self.ai_engine.explain(ctx)

            # 7. Merge and Authority Lock
            final_error_type = static_res.error_type
            final_severity = static_res.severity
            final_location = static_res.location
            
            # Build Result
            result = AnalysisResult(
                analysis_id=str(uuid.uuid4()),
                created_at=datetime.now(timezone.utc).isoformat(),
                language=request.language.value,
                error_type=final_error_type.value,
                severity=final_severity.value,
                location=final_location,
                summary=f"{final_error_type.value} detected" if primary else "Unknown Error",
                confidence=confidence,
                confidence_basis=["static"] if primary else [],
                static_findings=unique_findings,
                ai_suggestions=ai_outcome.suggestions if ai_outcome else [],
                provenance={
                    "error_type": "static" if primary else "derived",
                    "severity": "static" if primary else "derived",
                    "location": "static" if primary and primary.location else "derived"
                },
                ai_status=ai_outcome.status if ai_outcome else AIStatus.DISABLED,
                analysis_metadata=AnalysisMetadata(
                    analysis_mode="hybrid",
                    analyzers_run=analyzers_run,
                    analyzer_errors=analyzer_errors,
                    history_saved=False
                )
            )
            
            # Save history
            try:
                saved = self.history.save(result)
                result.analysis_metadata.history_saved = saved
            except Exception:
                result.analysis_metadata.history_saved = False
                
            return result

        except Exception as e:
            # Catch pipeline level exceptions and return valid result
            analyzer_errors.append(f"Pipeline error: {type(e).__name__}: {str(e)}")
            return AnalysisResult(
                analysis_id=str(uuid.uuid4()),
                created_at=datetime.now(timezone.utc).isoformat(),
                language=request.language.value,
                error_type=ErrorType.UNKNOWN.value,
                severity=Severity.UNKNOWN.value,
                summary="Analysis failed due to internal pipeline error",
                ai_status=AIStatus.DISABLED,
                analysis_metadata=AnalysisMetadata(
                    analysis_mode="static_only",
                    analyzers_run=analyzers_run,
                    analyzer_errors=analyzer_errors,
                    history_saved=False
                )
            )
