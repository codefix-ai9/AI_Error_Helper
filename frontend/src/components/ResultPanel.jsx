import React, { useState } from 'react';
import { ProvenanceBadge } from './ProvenanceBadge';
import { AIUnavailableBanner } from './AIUnavailableBanner';
import { DiffView } from './DiffView';
import { copyToClipboard } from '../utils/clipboard';
import { exportAsJSON, exportAsPlainText } from '../utils/export';

/**
 * ResultPanel component strictly implementing §10 result presentation.
 * @param {{
 *   result: Object,
 *   onClose?: () => void
 * }} props
 */
export function ResultPanel({ result, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const {
    error_type,
    severity,
    location,
    confidence,
    confidence_basis = [],
    uncertainty_note,
    summary,
    explanation,
    probable_cause,
    affected_code,
    corrected_code,
    correction_diff,
    debugging_steps = [],
    prevention_tip,
    key_concept,
    static_findings = [],
    ai_suggestions = [],
    verification,
    provenance = {},
    ai_status = 'ok',
    analysis_metadata = {}
  } = result;

  const handleCopySummary = async () => {
    const success = await copyToClipboard(
      `[${severity}] ${error_type}: ${summary}\n\nExplanation: ${explanation}\n\nSuggested Fix:\n${corrected_code}`
    );
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getSeverityClass = (sev) => {
    switch ((sev || '').toUpperCase()) {
      case 'CRITICAL': return 'sev-critical';
      case 'HIGH': return 'sev-high';
      case 'MEDIUM': return 'sev-medium';
      case 'LOW': return 'sev-low';
      default: return 'sev-unknown';
    }
  };

  return (
    <section className="result-panel" aria-label="Analysis Results">
      {/* Top action toolbar */}
      <div className="result-toolbar">
        <div className="toolbar-left">
          <h2 className="result-header-title">Diagnostic & Educational Result</h2>
          {ai_status === 'mock' && (
            <span className="badge-mock-indicator">
              ⚡ MOCK MODE (Simulated AI)
            </span>
          )}
        </div>
        <div className="toolbar-actions">
          <button
            type="button"
            className="action-btn"
            onClick={handleCopySummary}
            title="Copy summary and fix to clipboard"
          >
            {copied ? '✓ Copied!' : '📋 Copy'}
          </button>
          <button
            type="button"
            className="action-btn"
            onClick={() => exportAsJSON(result)}
            title="Download result as JSON"
          >
            💾 Export JSON
          </button>
          <button
            type="button"
            className="action-btn"
            onClick={() => exportAsPlainText(result)}
            title="Download result as Text Report"
          >
            📄 Export Text
          </button>
          {onClose && (
            <button
              type="button"
              className="action-btn close-btn"
              onClick={onClose}
              aria-label="Close results"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* §7.7 Fallback Banner if AI is unavailable/disabled/timeout */}
      <AIUnavailableBanner aiStatus={ai_status} />

      {/* 1. Chips: Category · Severity · Location · Confidence */}
      <div className="chips-container" role="region" aria-label="Error Overview Chips">
        <div className="chip chip-category">
          <span className="chip-label">Category:</span>
          <strong className="chip-value">{error_type || 'Unknown / Requires Review'}</strong>
          <ProvenanceBadge provenance={provenance.error_type || 'static'} />
        </div>

        <div className={`chip chip-severity ${getSeverityClass(severity)}`}>
          <span className="chip-label">Severity:</span>
          <strong className="chip-value">{severity || 'UNKNOWN'}</strong>
          <ProvenanceBadge provenance={provenance.severity || 'static'} />
        </div>

        <div className="chip chip-location">
          <span className="chip-label">Location:</span>
          <strong className="chip-value">
            Line {location?.line ?? '?'}{location?.column ? ` : Col ${location.column}` : ''}
          </strong>
          <ProvenanceBadge provenance={provenance.location || 'static'} />
        </div>

        <div className="chip chip-confidence">
          <span className="chip-label">Confidence:</span>
          <strong className="chip-value">
            {confidence != null ? `${Math.round(confidence * 100)}%` : 'N/A'}
          </strong>
          <ProvenanceBadge provenance="derived" label="DERIVED SCORE" />
        </div>
      </div>

      {/* One line summary */}
      {summary && (
        <div className="summary-banner">
          <span className="summary-icon">💡</span>
          <p className="summary-text">{summary}</p>
        </div>
      )}

      {/* 2. Detected by Static Analysis (facts) */}
      <div className="result-section static-facts-section">
        <div className="section-header">
          <div className="section-title-wrap">
            <span className="section-icon">⚙️</span>
            <h3 className="section-title">Detected by Static Analysis (Authoritative Facts)</h3>
          </div>
          <ProvenanceBadge provenance="static" label="DETERMINISTIC FACT" />
        </div>

        {static_findings && static_findings.length > 0 ? (
          <div className="findings-list">
            {static_findings.map((f, idx) => (
              <div key={idx} className="finding-item">
                <div className="finding-meta">
                  <span className="finding-rule-id">[{f.rule_id || 'RULE'}]</span>
                  <span className="finding-evidence-level">Evidence: {f.evidence_level}</span>
                  {f.location?.line && (
                    <span className="finding-loc">Line {f.location.line}:{f.location.column ?? 0}</span>
                  )}
                </div>
                <p className="finding-message">{f.message}</p>
                {f.snippet && (
                  <pre className="finding-snippet">
                    <code>{f.snippet}</code>
                  </pre>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-notice">No individual static rule violations detected; review general syntax and runtime context.</p>
        )}
      </div>

      {/* 3. AI-Assisted Explanation */}
      <div className="result-section ai-explanation-section">
        <div className="section-header">
          <div className="section-title-wrap">
            <span className="section-icon">✨</span>
            <h3 className="section-title">Educational Explanation</h3>
          </div>
          <ProvenanceBadge provenance={provenance.explanation || 'ai'} />
        </div>
        <p className="explanation-text">{explanation || 'No detailed explanation available.'}</p>

        {ai_suggestions && ai_suggestions.length > 0 && (
          <div className="ai-suggestions-box">
            <span className="suggestions-title">Additional Insights:</span>
            <ul className="suggestions-list">
              {ai_suggestions.map((s, idx) => (
                <li key={idx} className="suggestion-item">
                  <span className="suggestion-kind">[{s.kind}]</span> {s.text}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 4. Probable Cause */}
      {probable_cause && (
        <div className="result-section probable-cause-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-icon">🔍</span>
              <h3 className="section-title">Probable Cause</h3>
            </div>
            <ProvenanceBadge provenance={provenance.explanation || 'ai'} />
          </div>
          <p className="cause-text">{probable_cause}</p>
        </div>
      )}

      {/* 5. Affected Code (with detected line highlighted) */}
      {affected_code && (
        <div className="result-section affected-code-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-icon">📍</span>
              <h3 className="section-title">Affected Code Region</h3>
            </div>
            <ProvenanceBadge provenance="static" label="DETECTED LOCATION" />
          </div>
          <div className="code-display-box highlight-line">
            <pre className="code-pre">
              <code>{affected_code}</code>
            </pre>
          </div>
        </div>
      )}

      {/* 6. Suggested Correction + Diff View + Verification Note */}
      {corrected_code && (
        <div className="result-section correction-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-icon">🛠️</span>
              <h3 className="section-title">Suggested Correction</h3>
            </div>
            <ProvenanceBadge provenance={provenance.corrected_code || 'ai'} />
          </div>

          <DiffView
            originalCode={affected_code || ''}
            correctedCode={corrected_code}
            diffData={correction_diff}
          />

          {verification && (
            <div className="verification-card">
              <div className="verification-status">
                <span className="verification-icon">
                  {verification.corrected_code_parses ? '✅' : '⚠️'}
                </span>
                <span className="verification-title">
                  Syntax Validation: {verification.corrected_code_parses ? 'Passes static re-check' : 'Syntax check pending'}
                </span>
              </div>
              <p className="verification-note">{verification.note}</p>
            </div>
          )}
        </div>
      )}

      {/* 7. Debugging Steps */}
      {debugging_steps && debugging_steps.length > 0 && (
        <div className="result-section debugging-steps-section">
          <div className="section-header">
            <div className="section-title-wrap">
              <span className="section-icon">🪜</span>
              <h3 className="section-title">Step-by-Step Debugging Guide</h3>
            </div>
            <ProvenanceBadge provenance={provenance.debugging_steps || 'ai'} />
          </div>
          <ol className="steps-ordered-list">
            {debugging_steps.map((step, idx) => (
              <li key={idx} className="step-item">
                <span className="step-number">{idx + 1}</span>
                <span className="step-text">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* 8. Prevention Tip & Key Concept */}
      <div className="result-grid-two">
        {prevention_tip && (
          <div className="result-section prevention-section">
            <div className="section-header">
              <div className="section-title-wrap">
                <span className="section-icon">🛡️</span>
                <h3 className="section-title">Prevention Tip</h3>
              </div>
              <ProvenanceBadge provenance={provenance.prevention_tip || 'ai'} />
            </div>
            <p className="prevention-text">{prevention_tip}</p>
          </div>
        )}

        {key_concept && (
          <div className="result-section concept-section">
            <div className="section-header">
              <div className="section-title-wrap">
                <span className="section-icon">🧠</span>
                <h3 className="section-title">Key Computer Science Concept</h3>
              </div>
              <ProvenanceBadge provenance="derived" label="CORE CONCEPT" />
            </div>
            <p className="concept-text">{key_concept}</p>
          </div>
        )}
      </div>

      {/* 9. Uncertainty & Confidence Basis */}
      <div className="result-section uncertainty-section">
        <div className="section-header">
          <div className="section-title-wrap">
            <span className="section-icon">📊</span>
            <h3 className="section-title">Confidence & Uncertainty Note</h3>
          </div>
          <ProvenanceBadge provenance="derived" />
        </div>
        <p className="uncertainty-text">{uncertainty_note || 'Confidence based on combination of static parser rules and heuristics.'}</p>
        {confidence_basis && confidence_basis.length > 0 && (
          <div className="basis-pills">
            <span className="basis-label">Evidence Basis:</span>
            {confidence_basis.map((b, i) => (
              <span key={i} className="basis-pill">{b}</span>
            ))}
          </div>
        )}
      </div>

      {/* Metadata footer */}
      {analysis_metadata && (
        <footer className="result-metadata-footer">
          <span>Mode: <code>{analysis_metadata.analysis_mode || 'hybrid'}</code></span>
          <span>Latency: <code>{analysis_metadata.ai_latency_ms ?? 0}ms</code></span>
          <span>Pipeline: <code>v{analysis_metadata.pipeline_version || '1.0'}</code></span>
          <span>Provider: <code>{analysis_metadata.provider || 'mock'}</code></span>
          <span>Model: <code>{analysis_metadata.model || 'canned'}</code></span>
        </footer>
      )}
    </section>
  );
}
