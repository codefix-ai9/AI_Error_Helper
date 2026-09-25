import { describe, it, expect } from 'vitest';
import pythonFixture from '../fixtures/python_name_error.json';
import jsFixture from '../fixtures/javascript_type_error.json';
import syntaxFixture from '../fixtures/syntax_error_fallback.json';

describe('Contract Fixtures (§5.3 conformance)', () => {
  const fixtures = [
    { name: 'python_name_error', data: pythonFixture, expectedStatus: 'ok' },
    { name: 'javascript_type_error', data: jsFixture, expectedStatus: 'mock' },
    { name: 'syntax_error_fallback', data: syntaxFixture, expectedStatus: 'unavailable' }
  ];

  it('verifies all three fixtures exist and have required schema fields', () => {
    expect(fixtures.length).toBe(3);

    for (const { name, data, expectedStatus } of fixtures) {
      expect(data.schema_version, `${name} schema_version`).toBe('1.0');
      expect(data.analysis_id, `${name} analysis_id`).toBeDefined();
      expect(data.language, `${name} language`).toBeDefined();
      expect(data.error_type, `${name} error_type`).toBeDefined();
      expect(data.severity, `${name} severity`).toBeDefined();
      expect(data.location, `${name} location`).toBeDefined();
      expect(data.location.line, `${name} location.line`).toBeTypeOf('number');
      expect(data.summary, `${name} summary`).toBeDefined();
      expect(data.explanation, `${name} explanation`).toBeDefined();
      expect(data.corrected_code, `${name} corrected_code`).toBeDefined();
      expect(data.debugging_steps, `${name} debugging_steps`).toBeInstanceOf(Array);
      expect(data.debugging_steps.length, `${name} debugging_steps count`).toBeGreaterThanOrEqual(3);
      expect(data.static_findings, `${name} static_findings`).toBeInstanceOf(Array);
      expect(data.static_findings.length, `${name} static_findings count`).toBeGreaterThan(0);
      expect(data.provenance, `${name} provenance`).toBeDefined();
      expect(data.provenance.error_type, `${name} provenance.error_type`).toBe('static');
      expect(data.provenance.severity, `${name} provenance.severity`).toBe('static');
      expect(data.ai_status, `${name} ai_status`).toBe(expectedStatus);
      expect(data.verification, `${name} verification`).toBeDefined();
      expect(data.verification.corrected_code_parses, `${name} verification.corrected_code_parses`).toBe(true);
    }
  });

  it('ensures Fixture 3 contains verbatim fallback banner text', () => {
    const bannerWarning = syntaxFixture.analysis_metadata.warnings.find(w =>
      w.includes('AI explanation is unavailable. Showing deterministic static analysis findings only.')
    );
    expect(bannerWarning).toBe('AI explanation is unavailable. Showing deterministic static analysis findings only.');
  });
});
