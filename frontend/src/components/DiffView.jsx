import React, { useState } from 'react';

/**
 * Side-by-side or unified diff viewer.
 * @param {{
 *   originalCode: string,
 *   correctedCode: string,
 *   diffData?: {
 *     changed_lines_before?: number[],
 *     changed_lines_after?: number[],
 *     unified?: string
 *   }
 * }} props
 */
export function DiffView({ originalCode = '', correctedCode = '', diffData }) {
  const [viewMode, setViewMode] = useState('split'); // 'split' | 'unified'

  const origLines = (originalCode || '').split('\n');
  const corrLines = (correctedCode || '').split('\n');

  return (
    <div className="diff-view-container">
      <div className="diff-header">
        <span className="diff-title">Suggested Code Changes</span>
        <div className="diff-mode-toggle" role="group" aria-label="Diff view options">
          <button
            type="button"
            className={`toggle-btn ${viewMode === 'split' ? 'active' : ''}`}
            onClick={() => setViewMode('split')}
          >
            Side-by-Side
          </button>
          <button
            type="button"
            className={`toggle-btn ${viewMode === 'unified' ? 'active' : ''}`}
            onClick={() => setViewMode('unified')}
          >
            Unified Diff
          </button>
        </div>
      </div>

      {viewMode === 'split' ? (
        <div className="split-diff-grid">
          <div className="diff-pane diff-pane-before">
            <div className="diff-pane-label">
              <span className="diff-tag diff-tag-before">- Original / Affected Code</span>
            </div>
            <pre className="diff-code-block">
              {origLines.map((line, idx) => (
                <div key={idx} className="diff-line diff-line-removed">
                  <span className="line-num">{idx + 1}</span>
                  <span className="diff-marker">-</span>
                  <span className="line-text">{line || ' '}</span>
                </div>
              ))}
            </pre>
          </div>

          <div className="diff-pane diff-pane-after">
            <div className="diff-pane-label">
              <span className="diff-tag diff-tag-after">+ Corrected Code</span>
            </div>
            <pre className="diff-code-block">
              {corrLines.map((line, idx) => (
                <div key={idx} className="diff-line diff-line-added">
                  <span className="line-num">{idx + 1}</span>
                  <span className="diff-marker">+</span>
                  <span className="line-text">{line || ' '}</span>
                </div>
              ))}
            </pre>
          </div>
        </div>
      ) : (
        <div className="unified-diff-container">
          <pre className="unified-diff-code">
            {diffData?.unified || (
              <>
                {origLines.map((l, i) => (
                  <div key={`u-del-${i}`} className="diff-line diff-line-removed">
                    <span className="diff-marker">-</span> {l}
                  </div>
                ))}
                {corrLines.map((l, i) => (
                  <div key={`u-add-${i}`} className="diff-line diff-line-added">
                    <span className="diff-marker">+</span> {l}
                  </div>
                ))}
              </>
            )}
          </pre>
        </div>
      )}
    </div>
  );
}
