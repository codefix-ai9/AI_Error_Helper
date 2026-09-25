/**
 * @file JSDoc Type Definitions for Part B Dashboard and Data Models
 * Strictly aligns with §5.1 - §5.3 contracts.
 */

/**
 * @typedef {'python' | 'java' | 'javascript'} Language
 */

/**
 * @typedef {'Syntax' | 'Runtime' | 'Type' | 'Logic' | 'Name / Reference' | 'Dependency' | 'Configuration' | 'Indentation' | 'Import' | 'Unknown / Requires Review'} ErrorType
 */

/**
 * @typedef {'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN'} Severity
 */

/**
 * @typedef {'CONFIRMED' | 'PATTERN' | 'HEURISTIC' | 'NONE'} EvidenceLevel
 */

/**
 * @typedef {'ok' | 'mock' | 'disabled' | 'unavailable' | 'timeout' | 'invalid_response'} AIStatus
 */

/**
 * @typedef {'static' | 'ai' | 'derived'} Provenance
 */

/**
 * @typedef {Object} CodeLocation
 * @property {number} line
 * @property {number|null} [column]
 * @property {number|null} [end_line]
 */

/**
 * @typedef {Object} StaticFinding
 * @property {string} rule_id
 * @property {string} category
 * @property {EvidenceLevel} evidence_level
 * @property {string} source
 * @property {string} message
 * @property {CodeLocation} location
 * @property {string} snippet
 * @property {string} concept
 */

/**
 * @typedef {Object} AISuggestion
 * @property {'explanation' | 'correction' | 'debug_step' | 'prevention' | 'suggested_category'} kind
 * @property {string} text
 * @property {'ai'} provenance
 */

/**
 * @typedef {Object} VerificationInfo
 * @property {boolean} corrected_code_parses
 * @property {boolean} original_finding_resolved
 * @property {string} note
 */

/**
 * @typedef {Object} AnalysisResult
 * @property {string} schema_version - Always "1.0"
 * @property {string} analysis_id - UUID4
 * @property {string} created_at - ISO 8601 UTC
 * @property {Language} language
 * @property {ErrorType} error_type
 * @property {Severity} severity
 * @property {CodeLocation} location
 * @property {string} summary - Max 120 chars
 * @property {string} explanation
 * @property {string} probable_cause
 * @property {string} affected_code
 * @property {string} corrected_code
 * @property {{ changed_lines_before: number[], changed_lines_after: number[], unified: string }} correction_diff
 * @property {string[]} debugging_steps - 3 to 8 items
 * @property {string} prevention_tip
 * @property {string} key_concept
 * @property {number} confidence - 0.0 to 1.0
 * @property {string[]} confidence_basis
 * @property {string} uncertainty_note
 * @property {StaticFinding[]} static_findings
 * @property {AISuggestion[]} ai_suggestions
 * @property {VerificationInfo} verification
 * @property {Record<string, Provenance>} provenance
 * @property {AIStatus} ai_status
 * @property {Object} analysis_metadata
 */
