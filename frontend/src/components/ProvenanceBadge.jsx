import React from 'react';

/**
 * Renders a provenance badge (static, ai, or derived).
 * Adheres to accessibility requirements: never relies on color alone.
 * @param {{ provenance: 'static'|'ai'|'derived', label?: string }} props
 */
export function ProvenanceBadge({ provenance = 'static', label }) {
  const norm = (provenance || 'static').toLowerCase();
  
  let icon = '⚙️';
  let badgeClass = 'badge-static';
  let text = label || 'STATIC FACT';

  if (norm === 'ai') {
    icon = '✨';
    badgeClass = 'badge-ai';
    text = label || 'AI ASSISTED';
  } else if (norm === 'derived') {
    icon = '🔗';
    badgeClass = 'badge-derived';
    text = label || 'DERIVED';
  }

  return (
    <span className={`provenance-badge ${badgeClass}`} title={`Provenance: ${text}`}>
      <span aria-hidden="true" className="badge-icon">{icon}</span>
      <span className="badge-text">{text}</span>
    </span>
  );
}
