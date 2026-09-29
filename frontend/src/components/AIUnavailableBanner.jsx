import React from 'react';

/**
 * Banner shown when AI status is disabled, unavailable, timeout, or invalid_response.
 * Displays the §7.7 banner text verbatim.
 * @param {{ aiStatus: string }} props
 */
export function AIUnavailableBanner({ aiStatus }) {
  const isFallback = ['disabled', 'unavailable', 'timeout', 'invalid_response'].includes(aiStatus);

  if (!isFallback) return null;

  return (
    <div className="ai-unavailable-banner" role="status" aria-live="polite">
      <span className="banner-icon" aria-hidden="true">⚠️</span>
      <div className="banner-content">
        <strong className="banner-title">
          AI explanation is unavailable. Showing deterministic static analysis findings only.
        </strong>
        <span className="banner-subtitle">
          (Reason: Provider status is <code>{aiStatus}</code>. Core static analysis and compiler findings remain 100% active.)
        </span>
      </div>
    </div>
  );
}
