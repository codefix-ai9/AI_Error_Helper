import { describe, it, expect } from 'vitest';
import { validateAnalysisInput, MAX_SOURCE_CHARS, MAX_ERROR_CHARS } from '../utils/validation';

describe('Client-Side Validation (§5.6)', () => {
  it('fails when language is missing', () => {
    const res = validateAnalysisInput({
      language: '',
      source_code: 'print("hello")',
      error_input: 'some error'
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.language).toBe('Please select a programming language.');
  });

  it('fails when language is unsupported', () => {
    const res = validateAnalysisInput({
      language: 'ruby',
      source_code: 'puts "hello"',
      error_input: 'some error'
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.language).toBe("Language 'ruby' is not supported yet. Supported: python, java, javascript.");
  });

  it('fails when source code is blank', () => {
    const res = validateAnalysisInput({
      language: 'python',
      source_code: '   ',
      error_input: 'some error'
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.source_code).toBe('Please provide the source code before analysis.');
  });

  it('fails when error input is blank', () => {
    const res = validateAnalysisInput({
      language: 'python',
      source_code: 'print(x)',
      error_input: ''
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.error_input).toBe('Please provide the compiler/runtime error or observed problem.');
  });

  it('fails when source code exceeds character limit (20,000)', () => {
    const oversized = 'a'.repeat(MAX_SOURCE_CHARS + 1);
    const res = validateAnalysisInput({
      language: 'python',
      source_code: oversized,
      error_input: 'some error'
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.source_code).toBe('Source code is too large (max 20,000 characters).');
  });

  it('fails when error text exceeds character limit (10,000)', () => {
    const oversized = 'e'.repeat(MAX_ERROR_CHARS + 1);
    const res = validateAnalysisInput({
      language: 'python',
      source_code: 'print(1)',
      error_input: oversized
    });
    expect(res.isValid).toBe(false);
    expect(res.errors.error_input).toBe('Error text is too large (max 10,000 characters).');
  });

  it('passes on valid input across supported languages', () => {
    for (const lang of ['python', 'java', 'javascript']) {
      const res = validateAnalysisInput({
        language: lang,
        source_code: 'console.log("ok");',
        error_input: 'ReferenceError: x is not defined'
      });
      expect(res.isValid).toBe(true);
      expect(Object.keys(res.errors).length).toBe(0);
    }
  });
});
