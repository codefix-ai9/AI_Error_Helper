import React, { useRef, useEffect } from 'react';
import { MAX_SOURCE_CHARS } from '../utils/validation';

/**
 * CodeInput component with synchronized line numbers and character limits.
 * @param {{
 *   value: string,
 *   onChange: (val: string) => void,
 *   error?: string,
 *   disabled?: boolean
 * }} props
 */
export function CodeInput({ value = '', onChange, error, disabled = false }) {
  const lineNumbersRef = useRef(null);
  const textareaRef = useRef(null);

  const lines = value.split('\n');
  const lineCount = lines.length;

  const handleScroll = () => {
    if (lineNumbersRef.current && textareaRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const charCount = value.length;
  const isNearLimit = charCount > MAX_SOURCE_CHARS * 0.9;
  const isOverLimit = charCount > MAX_SOURCE_CHARS;

  return (
    <div className={`code-input-container ${error ? 'has-error' : ''}`}>
      <div className="input-toolbar">
        <label htmlFor="source-code-editor" className="input-label">
          Source Code <span className="required-star">*</span>
        </label>
        <span className={`char-counter ${isOverLimit ? 'limit-exceeded' : isNearLimit ? 'limit-warning' : ''}`}>
          {charCount.toLocaleString()} / {MAX_SOURCE_CHARS.toLocaleString()} chars
        </span>
      </div>

      <div className="editor-wrapper">
        <div className="line-numbers" ref={lineNumbersRef} aria-hidden="true">
          {Array.from({ length: Math.max(lineCount, 1) }, (_, i) => (
            <div key={i + 1} className="line-number">
              {i + 1}
            </div>
          ))}
        </div>

        <textarea
          id="source-code-editor"
          ref={textareaRef}
          className="code-textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onScroll={handleScroll}
          placeholder="// Paste or write your source code here..."
          disabled={disabled}
          spellCheck={false}
          autoCapitalize="off"
          autoComplete="off"
          autoCorrect="off"
          aria-invalid={!!error}
          aria-describedby={error ? 'source-code-error' : undefined}
        />
      </div>

      {error && (
        <p id="source-code-error" className="field-error-message" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
