import React from 'react';
import { MAX_ERROR_CHARS } from '../utils/validation';

/**
 * ErrorInput component for compiler/runtime/traceback/console messages.
 * @param {{
 *   value: string,
 *   onChange: (val: string) => void,
 *   error?: string,
 *   disabled?: boolean
 * }} props
 */
export function ErrorInput({ value = '', onChange, error, disabled = false }) {
  const charCount = value.length;
  const isNearLimit = charCount > MAX_ERROR_CHARS * 0.9;
  const isOverLimit = charCount > MAX_ERROR_CHARS;

  return (
    <div className={`error-input-container ${error ? 'has-error' : ''}`}>
      <div className="input-toolbar">
        <label htmlFor="error-console-editor" className="input-label">
          Compiler / Runtime Error or Observed Problem <span className="required-star">*</span>
        </label>
        <span className={`char-counter ${isOverLimit ? 'limit-exceeded' : isNearLimit ? 'limit-warning' : ''}`}>
          {charCount.toLocaleString()} / {MAX_ERROR_CHARS.toLocaleString()} chars
        </span>
      </div>

      <textarea
        id="error-console-editor"
        className="error-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your compiler traceback, runtime exception, terminal output, or describe what went wrong..."
        disabled={disabled}
        spellCheck={false}
        rows={8}
        aria-invalid={!!error}
        aria-describedby={error ? 'error-input-error' : undefined}
      />

      {error && (
        <p id="error-input-error" className="field-error-message" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
