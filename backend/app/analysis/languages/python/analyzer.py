from typing import List
from backend.app.analysis.registry import LanguageAnalyzer, register_analyzer
from backend.app.models.stages import NormalizedInput, Finding
from backend.app.models.enums import Language
from backend.app.analysis.languages.python.ast_parser import parse_ast_for_errors
from backend.app.analysis.languages.python.traceback_parser import parse_traceback
from backend.app.analysis.rules.engine import RuleEngine, load_rules

class PythonAnalyzer(LanguageAnalyzer):
    def __init__(self):
        self.rule_engine = RuleEngine(load_rules('python'))
        
    def analyze(self, input_data: NormalizedInput) -> List[Finding]:
        all_findings = []
        
        # AST
        ast_f, _ = parse_ast_for_errors(input_data.source_code)
        if ast_f:
            all_findings.append(ast_f)
            
        # Traceback
        tb_f, _ = parse_traceback(input_data.error_text_clean)
        if tb_f:
            all_findings.append(tb_f)
            
        # Rule Engine
        re_f, _ = self.rule_engine.evaluate(input_data.error_text_clean, input_data.source_code)
        if re_f:
            all_findings.append(re_f)
            
        return all_findings

# Register it
register_analyzer(Language.PYTHON, PythonAnalyzer())
