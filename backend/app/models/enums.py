from enum import Enum

class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"

class ErrorType(str, Enum):
    SYNTAX = "Syntax"
    RUNTIME = "Runtime"
    TYPE = "Type"
    LOGIC = "Logic"
    NAME_REFERENCE = "Name / Reference"
    DEPENDENCY = "Dependency"
    CONFIGURATION = "Configuration"
    INDENTATION = "Indentation"
    IMPORT = "Import"
    UNKNOWN = "Unknown / Requires Review"

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class EvidenceLevel(str, Enum):
    CONFIRMED = "CONFIRMED"
    PATTERN = "PATTERN"
    HEURISTIC = "HEURISTIC"
    NONE = "NONE"

class AIStatus(str, Enum):
    OK = "ok"
    MOCK = "mock"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"

class Provenance(str, Enum):
    STATIC = "static"
    AI = "ai"
    DERIVED = "derived"
