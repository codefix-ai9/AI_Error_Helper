/**
 * Export helpers for saving results as JSON or plain text.
 */

/**
 * Downloads a string as a file.
 * @param {string} content
 * @param {string} filename
 * @param {string} mimeType
 */
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Exports analysis result as formatted JSON file.
 * @param {Object} result
 */
export function exportAsJSON(result) {
  const filename = `analysis-${result?.analysis_id || 'result'}.json`;
  const jsonStr = JSON.stringify(result, null, 2);
  downloadFile(jsonStr, filename, 'application/json');
}

/**
 * Exports analysis result as human-readable plain text.
 * @param {Object} result
 */
export function exportAsPlainText(result) {
  if (!result) return;
  const filename = `analysis-${result.analysis_id || 'result'}.txt`;
  const lines = [
    `AI-BASED PROGRAMMING ERROR HELPER - ANALYSIS REPORT`,
    `====================================================`,
    `Analysis ID : ${result.analysis_id || 'N/A'}`,
    `Date (UTC)  : ${result.created_at || new Date().toISOString()}`,
    `Language    : ${result.language?.toUpperCase()}`,
    `Category    : ${result.error_type}`,
    `Severity    : ${result.severity}`,
    `Location    : Line ${result.location?.line || 'N/A'}, Col ${result.location?.column || 'N/A'}`,
    `Confidence  : ${Math.round((result.confidence || 0) * 100)}% (${(result.confidence_basis || []).join(', ')})`,
    `AI Status   : ${result.ai_status}`,
    ``,
    `SUMMARY:`,
    result.summary || 'N/A',
    ``,
    `STATIC FINDINGS:`,
    ...(result.static_findings || []).map(f => `  • [${f.rule_id || 'RULE'}] (${f.evidence_level}) ${f.message}`),
    ``,
    `EXPLANATION:`,
    result.explanation || 'N/A',
    ``,
    `PROBABLE CAUSE:`,
    result.probable_cause || 'N/A',
    ``,
    `CORRECTED CODE:`,
    result.corrected_code || 'N/A',
    ``,
    `DEBUGGING STEPS:`,
    ...(result.debugging_steps || []).map((s, idx) => `  ${idx + 1}. ${s}`),
    ``,
    `PREVENTION TIP:`,
    result.prevention_tip || 'N/A',
    ``,
    `KEY CONCEPT:`,
    result.key_concept || 'N/A',
    ``,
    `VERIFICATION NOTE:`,
    result.verification?.note || 'N/A',
    `====================================================`
  ];

  downloadFile(lines.join('\n'), filename, 'text/plain');
}
