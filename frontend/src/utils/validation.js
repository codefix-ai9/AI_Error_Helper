/**
 * Client-side validation adhering strictly to specification §5.6.
 */

export const SUPPORTED_LANGUAGES = ['python', 'java', 'javascript'];
export const MAX_SOURCE_CHARS = 20000;
export const MAX_ERROR_CHARS = 10000;

/**
 * Validates analysis input according to §5.6 rules.
 * @param {Object} input
 * @param {string} [input.language]
 * @param {string} [input.source_code]
 * @param {string} [input.error_input]
 * @returns {{ isValid: boolean, errors: Record<string, string> }}
 */
export function validateAnalysisInput(input = {}) {
  const errors = {};

  // 1. Language validation
  if (!input.language || typeof input.language !== 'string' || input.language.trim() === '') {
    errors.language = 'Please select a programming language.';
  } else {
    const lang = input.language.trim().toLowerCase();
    if (!SUPPORTED_LANGUAGES.includes(lang)) {
      errors.language = `Language '${input.language}' is not supported yet. Supported: python, java, javascript.`;
    }
  }

  // 2. Source code non-blank validation
  if (!input.source_code || typeof input.source_code !== 'string' || input.source_code.trim() === '') {
    errors.source_code = 'Please provide the source code before analysis.';
  } else if (input.source_code.length > MAX_SOURCE_CHARS) {
    errors.source_code = `Source code is too large (max ${MAX_SOURCE_CHARS.toLocaleString()} characters).`;
  }

  // 3. Error input non-blank validation
  if (!input.error_input || typeof input.error_input !== 'string' || input.error_input.trim() === '') {
    errors.error_input = 'Please provide the compiler/runtime error or observed problem.';
  } else if (input.error_input.length > MAX_ERROR_CHARS) {
    errors.error_input = `Error text is too large (max ${MAX_ERROR_CHARS.toLocaleString()} characters).`;
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
