import pythonFixture from '../fixtures/python_name_error.json';
import jsFixture from '../fixtures/javascript_type_error.json';
import syntaxFixture from '../fixtures/syntax_error_fallback.json';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
export const USE_FIXTURES = import.meta.env.VITE_USE_FIXTURES === 'true';

export const FIXTURES = {
  python_name_error: pythonFixture,
  javascript_type_error: jsFixture,
  syntax_error_fallback: syntaxFixture
};

/**
 * Analyzes code either using local contract fixtures or the real backend.
 * @param {Object} payload
 * @param {string} payload.language
 * @param {string} payload.source_code
 * @param {string} payload.error_input
 * @param {string} [payload.expected_behavior]
 * @param {string} [fixtureKey]
 * @param {AbortSignal} [signal]
 * @returns {Promise<Object>} The analysis result data object
 */
export async function analyzeCode(payload, fixtureKey = null, signal = null) {
  if (USE_FIXTURES || fixtureKey) {
    // Simulate short network latency (150ms) for realistic UX
    await new Promise(resolve => setTimeout(resolve, 150));

    if (fixtureKey && FIXTURES[fixtureKey]) {
      return FIXTURES[fixtureKey];
    }
    // Select fixture based on language or fallback
    if (payload.language === 'javascript') {
      return FIXTURES.javascript_type_error;
    }
    if (payload.error_input?.toLowerCase().includes('syntax')) {
      return FIXTURES.syntax_error_fallback;
    }
    return FIXTURES.python_name_error;
  }

  // Real backend call
  const timeoutId = setTimeout(() => {
    // 45-second client timeout as required in §10
  }, 45000);

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      signal
    });

    clearTimeout(timeoutId);
    const envelope = await res.json();

    if (!envelope.success) {
      const err = new Error(envelope.error?.message || 'Analysis failed');
      err.code = envelope.error?.code;
      err.details = envelope.error?.details;
      err.requestId = envelope.error?.request_id;
      throw err;
    }

    return envelope.data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Analysis request was cancelled.');
    }
    throw err;
  }
}

/**
 * Health check endpoint
 */
export async function getHealth() {
  if (USE_FIXTURES) {
    return {
      status: 'ok',
      version: '1.0.0',
      ai_provider: 'mock',
      ai_configured: true,
      db_ok: true
    };
  }
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  const envelope = await res.json();
  return envelope.data;
}

/**
 * Fetch sample errors
 */
export async function getSamples() {
  if (USE_FIXTURES) {
    return [
      {
        id: 'sample-py-1',
        title: 'Python: NameError (undefined total)',
        language: 'python',
        source_code: 'def calculate():\n    print(total)\n    total = 10\n',
        error_input: "Traceback (most recent call last):\n  File 'main.py', line 2, in calculate\nNameError: name 'total' is not defined",
        fixtureKey: 'python_name_error'
      },
      {
        id: 'sample-js-1',
        title: 'JavaScript: TypeError (null object method)',
        language: 'javascript',
        source_code: 'function formatUser(user) {\n  return user.toLowerCase();\n}\nformatUser(null);',
        error_input: 'TypeError: user.toLowerCase is not a function at formatUser (app.js:2:15)',
        fixtureKey: 'javascript_type_error'
      },
      {
        id: 'sample-py-2',
        title: 'Python: SyntaxError (missing colon)',
        language: 'python',
        source_code: 'x = 15\nif x > 10\n    print("greater")\n',
        error_input: '  File "app.py", line 2\n    if x > 10\n            ^\nSyntaxError: expected \':\'',
        fixtureKey: 'syntax_error_fallback'
      }
    ];
  }
  const res = await fetch(`${API_BASE_URL}/api/v1/samples`);
  const envelope = await res.json();
  return envelope.data;
}

/**
 * Fetch analytics summary
 */
export async function getAnalyticsSummary() {
  if (USE_FIXTURES) {
    return {
      total: 42,
      by_error_type: {
        'Name / Reference': 15,
        'Type': 12,
        'Syntax': 9,
        'Runtime': 6
      },
      by_language: {
        'python': 24,
        'javascript': 12,
        'java': 6
      },
      by_severity: {
        'CRITICAL': 8,
        'HIGH': 16,
        'MEDIUM': 14,
        'LOW': 4
      },
      by_ai_status: {
        'ok': 30,
        'mock': 8,
        'unavailable': 4
      },
      daily_counts: [
        { date: '2026-09-20', count: 7 },
        { date: '2026-09-21', count: 11 },
        { date: '2026-09-22', count: 9 },
        { date: '2026-09-23', count: 8 },
        { date: '2026-09-24', count: 7 }
      ],
      recent: [
        FIXTURES.python_name_error,
        FIXTURES.javascript_type_error,
        FIXTURES.syntax_error_fallback
      ]
    };
  }
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/summary`);
  const envelope = await res.json();
  return envelope.data;
}

/**
 * Fetch history list
 */
export async function getHistory(params = {}) {
  if (USE_FIXTURES) {
    return {
      items: [
        FIXTURES.python_name_error,
        FIXTURES.javascript_type_error,
        FIXTURES.syntax_error_fallback
      ],
      total: 3
    };
  }
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE_URL}/api/v1/history?${query}`);
  const envelope = await res.json();
  return envelope.data;
}
