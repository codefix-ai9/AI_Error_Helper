import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { CodeInput } from './components/CodeInput';
import { ErrorInput } from './components/ErrorInput';
import { ResultPanel } from './components/ResultPanel';
import { HistoryView } from './components/HistoryView';
import { AnalyticsView } from './components/AnalyticsView';
import { validateAnalysisInput, SUPPORTED_LANGUAGES } from './utils/validation';
import { analyzeCode, getSamples, USE_FIXTURES } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState('analyze'); // 'analyze' | 'history' | 'analytics'
  const [language, setLanguage] = useState('python');
  const [sourceCode, setSourceCode] = useState('');
  const [errorInput, setErrorInput] = useState('');
  const [expectedBehavior, setExpectedBehavior] = useState('');
  const [selectedFixture, setSelectedFixture] = useState('');

  // Execution states
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [analysisResult, setAnalysisResult] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  // Sample errors for quick load
  const [sampleOptions, setSampleOptions] = useState([]);

  const abortControllerRef = useRef(null);

  useEffect(() => {
    // Load example presets
    getSamples()
      .then((samples) => {
        setSampleOptions(samples || []);
      })
      .catch((err) => {
        console.warn('Failed to load sample errors:', err);
      });
  }, []);

  const handleSelectSample = (sampleId) => {
    const found = sampleOptions.find(s => s.id === sampleId);
    if (!found) return;
    setLanguage(found.language);
    setSourceCode(found.source_code);
    setErrorInput(found.error_input);
    setSelectedFixture(found.fixtureKey || '');
    setValidationErrors({});
    setApiError(null);
  };

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault();

    // Client-side validation (§5.6)
    const validation = validateAnalysisInput({
      language,
      source_code: sourceCode,
      error_input: errorInput
    });

    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      setStatusMessage('Validation failed. Please correct input fields.');
      return;
    }

    setValidationErrors({});
    setApiError(null);
    setLoading(true);
    setStatusMessage('Analyzing code and processing diagnostics...');

    // Abort controller for cancel and timeout
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const payload = {
        language,
        source_code: sourceCode,
        error_input: errorInput,
        expected_behavior: expectedBehavior || undefined
      };

      const result = await analyzeCode(payload, selectedFixture || null, controller.signal);
      setAnalysisResult(result);
      setStatusMessage('Analysis complete.');
    } catch (err) {
      if (err.message === 'Analysis request was cancelled.') {
        setStatusMessage('Analysis cancelled by user.');
      } else {
        setApiError(err.message || 'An unexpected error occurred during analysis.');
        setStatusMessage('Error encountered.');
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const isMockActive = analysisResult?.ai_status === 'mock' || USE_FIXTURES;

  return (
    <div className="app-layout">
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        isMockMode={isMockActive}
        isFixtureMode={USE_FIXTURES}
      />

      <main className="app-main-content">
        {/* Screen-reader live region for dynamic announcements */}
        <div className="sr-only" aria-live="polite" role="status">
          {statusMessage}
        </div>

        {currentTab === 'history' && (
          <HistoryView
            onSelectResult={(item) => {
              setAnalysisResult(item);
              setCurrentTab('analyze');
            }}
          />
        )}

        {currentTab === 'analytics' && <AnalyticsView />}

        {currentTab === 'analyze' && (
          <div className="analyze-container">
            {/* Input Controls Bar */}
            <div className="analyze-top-bar">
              <div className="lang-select-group">
                <label htmlFor="language-select" className="bar-label">
                  Language <span className="required-star">*</span>
                </label>
                <select
                  id="language-select"
                  className={`bar-select ${validationErrors.language ? 'select-error' : ''}`}
                  value={language}
                  onChange={(e) => {
                    setLanguage(e.target.value);
                    if (validationErrors.language) {
                      setValidationErrors(prev => ({ ...prev, language: undefined }));
                    }
                  }}
                  disabled={loading}
                >
                  <option value="">-- Select Language --</option>
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang} value={lang}>
                      {lang.charAt(0).toUpperCase() + lang.slice(1)}
                    </option>
                  ))}
                </select>
                {validationErrors.language && (
                  <span className="inline-error">{validationErrors.language}</span>
                )}
              </div>

              {/* Sample loader helper */}
              <div className="samples-select-group">
                <label htmlFor="sample-preset-select" className="bar-label">
                  Load Example Scenario:
                </label>
                <select
                  id="sample-preset-select"
                  className="bar-select"
                  onChange={(e) => handleSelectSample(e.target.value)}
                  defaultValue=""
                  disabled={loading}
                >
                  <option value="" disabled>-- Choose a sample error --</option>
                  {sampleOptions.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.title}
                    </option>
                  ))}
                </select>
              </div>

              {/* Manual Fixture Switcher (B-M1 fixture verification) */}
              {USE_FIXTURES && (
                <div className="fixture-switcher-group">
                  <label htmlFor="fixture-select" className="bar-label">
                    Fixture Test:
                  </label>
                  <select
                    id="fixture-select"
                    className="bar-select fixture-select"
                    value={selectedFixture}
                    onChange={(e) => setSelectedFixture(e.target.value)}
                    disabled={loading}
                  >
                    <option value="">Auto by input</option>
                    <option value="python_name_error">Fixture 1: Python NameError (ok)</option>
                    <option value="javascript_type_error">Fixture 2: JS TypeError (mock)</option>
                    <option value="syntax_error_fallback">Fixture 3: Syntax Fallback (unavailable)</option>
                  </select>
                </div>
              )}
            </div>

            {/* Two-pane input grid */}
            <div className="input-panes-grid">
              <div className="input-pane">
                <CodeInput
                  value={sourceCode}
                  onChange={(val) => {
                    setSourceCode(val);
                    if (validationErrors.source_code) {
                      setValidationErrors(prev => ({ ...prev, source_code: undefined }));
                    }
                  }}
                  error={validationErrors.source_code}
                  disabled={loading}
                />
              </div>

              <div className="input-pane">
                <ErrorInput
                  value={errorInput}
                  onChange={(val) => {
                    setErrorInput(val);
                    if (validationErrors.error_input) {
                      setValidationErrors(prev => ({ ...prev, error_input: undefined }));
                    }
                  }}
                  error={validationErrors.error_input}
                  disabled={loading}
                />

                <div className="additive-input-container">
                  <label htmlFor="expected-behavior-input" className="input-label optional-label">
                    Expected Behavior <em>(optional)</em>
                  </label>
                  <input
                    id="expected-behavior-input"
                    type="text"
                    className="additive-input"
                    placeholder="Describe what the program should have outputted or achieved..."
                    value={expectedBehavior}
                    onChange={(e) => setExpectedBehavior(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            {/* Submit / Action Bar */}
            <div className="analyze-action-bar">
              <button
                type="button"
                id="analyze-submit-button"
                className="btn-primary-analyze"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-btn" aria-hidden="true"></span>
                    Analyzing Diagnostics...
                  </>
                ) : (
                  <>🔍 Run Hybrid Analysis</>
                )}
              </button>

              {loading && (
                <button
                  type="button"
                  id="analyze-cancel-button"
                  className="btn-cancel"
                  onClick={handleCancel}
                >
                  Cancel
                </button>
              )}
            </div>

            {/* Network / Backend Error with Retry */}
            {apiError && (
              <div className="api-error-card" role="alert">
                <span className="error-icon" aria-hidden="true">❌</span>
                <div className="error-body">
                  <strong>Analysis Request Failed</strong>
                  <p>{apiError}</p>
                </div>
                <button
                  type="button"
                  className="btn-retry"
                  onClick={handleAnalyze}
                >
                  ↻ Retry
                </button>
              </div>
            )}

            {/* Result Panel (Rendered upon success or fixture selection) */}
            {analysisResult && (
              <ResultPanel
                result={analysisResult}
                onClose={() => setAnalysisResult(null)}
              />
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p className="footer-privacy-note">
          🔒 <strong>Privacy &amp; Data Note (§7.8):</strong> Code submitted for analysis is processed locally and redacted before being forwarded to the configured AI provider. No credentials or secrets are logged.
        </p>
        <p className="footer-meta">
          AI-Based Programming Error Helper &bull; Milestone B-M1 Verified &bull; Schema v1.0
        </p>
      </footer>
    </div>
  );
}
export default App;
