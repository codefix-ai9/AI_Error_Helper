import json
import re
import os
from typing import List, Tuple, Optional, Dict, Any
from backend.app.models.stages import Finding, Location
from backend.app.models.enums import EvidenceLevel, ErrorType

def compute_confidence(evidence_level: EvidenceLevel, corroborated: bool = False, conflict: bool = False) -> Optional[float]:
    if evidence_level == EvidenceLevel.NONE:
        return None
        
    base = 0.0
    if evidence_level == EvidenceLevel.CONFIRMED:
        base = 0.90
    elif evidence_level == EvidenceLevel.PATTERN:
        base = 0.70
    elif evidence_level == EvidenceLevel.HEURISTIC:
        base = 0.40
        
    if corroborated:
        base += 0.05
    if conflict:
        base -= 0.15
        
    # Clamp between 0.05 and 0.95
    return max(0.05, min(0.95, base))

def load_rules(language: str) -> List[Dict[str, Any]]:
    # Load rules from json file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, f"{language}.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

class RuleEngine:
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules
        # Compile regexes ahead of time
        self.compiled_rules = []
        for rule in rules:
            try:
                compiled_pattern = re.compile(rule["pattern"])
                self.compiled_rules.append((rule, compiled_pattern))
            except Exception:
                # If regex is invalid, we skip it
                pass

    def evaluate(self, error_text: str, source_code: str = "") -> Tuple[Optional[Finding], List[str]]:
        analyzer_errors = []
        try:
            for rule, pattern in self.compiled_rules:
                target_type = rule.get("match_target", "error_text")
                target_str = source_code if target_type == "source_code" else error_text
                
                match = pattern.search(target_str)
                if match:
                    # Map strings to enums safely
                    evidence_str = rule.get("evidence_level", "PATTERN")
                    evidence_level = EvidenceLevel(evidence_str)
                    
                    error_type_str = rule.get("error_type", "Unknown / Requires Review")
                    
                    # Extract line number if we matched on source code using re.MULTILINE
                    location = Location()
                    if target_type == "source_code":
                        # Count newlines up to the match index to get the line number
                        line_number = target_str[:match.start()].count('\n') + 1
                        location = Location(line=line_number)
                    
                    return Finding(
                        rule_id=rule.get("id", "UNKNOWN"),
                        category=error_type_str,
                        evidence_level=evidence_level,
                        source="rule_engine",
                        message=match.group(0).strip(),
                        location=location
                    ), analyzer_errors
            return None, analyzer_errors
        except Exception as e:
            analyzer_errors.append(f"rule_engine internal error: {type(e).__name__}: {str(e)}")
            return None, analyzer_errors
