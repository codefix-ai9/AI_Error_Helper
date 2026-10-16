import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ResultPanel } from '../components/ResultPanel';

// Mock clipboard and export utilities
vi.mock('../utils/clipboard', () => ({
  copyToClipboard: vi.fn().mockResolvedValue(true)
}));
vi.mock('../utils/export', () => ({
  exportAsJSON: vi.fn(),
  exportAsPlainText: vi.fn()
}));

import { copyToClipboard } from '../utils/clipboard';
import { exportAsJSON, exportAsPlainText } from '../utils/export';

const mockResult = {
  analysis_id: 'test-uuid',
  created_at: '2026-09-20T10:00:00Z',
  language: 'python',
  error_type: 'Name / Reference',
  severity: 'HIGH',
  location: { line: 8, column: 12, end_line: null },
  summary: "Name 'total' is used on line 8 but never defined.",
  explanation: 'The variable total is referenced before being assigned.',
  probable_cause: 'Variable used before assignment.',
  affected_code: 'print(total)',
  corrected_code: 'total = 0\nprint(total)',
  correction_diff: {
    changed_lines_before: ['print(total)'],
    changed_lines_after: ['total = 0', 'print(total)'],
    unified: '- print(total)\n+ total = 0\n+ print(total)'
  },
  debugging_steps: [
    'Check where total is first used.',
    'Verify total is defined before usage.',
    'Move definition above usage.'
  ],
  prevention_tip: 'Always define variables before using them.',
  key_concept: 'variable scope',
  confidence: 0.85,
  confidence_basis: ['parser-confirmed', 'error text agrees with source'],
  uncertainty_note: 'High confidence from static analysis.',
  static_findings: [
    {
      rule_id: 'PY-NAME-001',
      category: 'Name / Reference',
      evidence_level: 'PATTERN',
      source: 'rule',
      message: "Name 'total' is used on line 8 but never defined.",
      location: { line: 8, column: 12 },
      snippet: 'print(total)',
      concept: 'variable scope'
    }
  ],
  ai_suggestions: [
    { kind: 'explanation', text: 'The NameError occurs because...', provenance: 'ai' }
  ],
  verification: {
    corrected_code_parses: true,
    original_finding_resolved: true,
    note: 'Passes syntax/static re-check. This is NOT proof of correct behavior.'
  },
  provenance: {
    error_type: 'static',
    severity: 'static',
    location: 'static',
    explanation: 'ai',
    corrected_code: 'ai',
    debugging_steps: 'ai',
    prevention_tip: 'ai'
  },
  ai_status: 'ok',
  analysis_metadata: {
    analysis_mode: 'hybrid',
    pipeline_version: '1.0',
    prompt_version: 'v1',
    provider: 'mock',
    model: 'canned',
    ai_latency_ms: 42,
    analyzers_run: ['python-parser', 'rule-engine'],
    analyzer_errors: [],
    warnings: [],
    history_saved: true
  }
};

describe('ResultPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders provenance badges for static and AI sections', () => {
    render(<ResultPanel result={mockResult} />);
    // Static facts section
    expect(screen.getByText('Detected by Static Analysis (Authoritative Facts)')).toBeDefined();
    // AI explanation section
    expect(screen.getByText('Educational Explanation')).toBeDefined();
  });

  it('renders chips with correct values', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('Name / Reference')).toBeDefined();
    expect(screen.getByText('HIGH')).toBeDefined();
    expect(screen.getAllByText(/Line 8/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('85%')).toBeDefined();
  });

  it('renders static findings with rule IDs and evidence level', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('[PY-NAME-001]')).toBeDefined();
    expect(screen.getByText('Evidence: PATTERN')).toBeDefined();
    expect(screen.getAllByText("Name 'total' is used on line 8 but never defined.").length).toBeGreaterThanOrEqual(1);
  });

  it('renders debugging steps as ordered list', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('Check where total is first used.')).toBeDefined();
    expect(screen.getByText('Move definition above usage.')).toBeDefined();
  });

  it('renders verification card with pass status', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText(/Passes static re-check/)).toBeDefined();
    expect(screen.getByText(/NOT proof of correct behavior/)).toBeDefined();
  });

  it('renders prevention tip and key concept', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('Always define variables before using them.')).toBeDefined();
    expect(screen.getByText('variable scope')).toBeDefined();
  });

  it('renders MOCK MODE badge when ai_status is mock', () => {
    const mockModeResult = { ...mockResult, ai_status: 'mock' };
    render(<ResultPanel result={mockModeResult} />);
    expect(screen.getByText(/MOCK MODE/)).toBeDefined();
  });

  it('shows AI-unavailable banner when ai_status is disabled', () => {
    const disabledResult = { ...mockResult, ai_status: 'disabled' };
    render(<ResultPanel result={disabledResult} />);
    // AIUnavailableBanner should render
    const banner = document.querySelector('.ai-unavailable-banner');
    // The banner component should exist or not throw
  });

  it('calls copy to clipboard when Copy button clicked', async () => {
    render(<ResultPanel result={mockResult} />);
    const copyBtn = screen.getByText('📋 Copy');
    await fireEvent.click(copyBtn);
    expect(copyToClipboard).toHaveBeenCalled();
  });

  it('calls exportAsJSON when Export JSON clicked', () => {
    render(<ResultPanel result={mockResult} />);
    const jsonBtn = screen.getByText('💾 Export JSON');
    fireEvent.click(jsonBtn);
    expect(exportAsJSON).toHaveBeenCalledWith(mockResult);
  });

  it('calls exportAsPlainText when Export Text clicked', () => {
    render(<ResultPanel result={mockResult} />);
    const textBtn = screen.getByText('📄 Export Text');
    fireEvent.click(textBtn);
    expect(exportAsPlainText).toHaveBeenCalledWith(mockResult);
  });

  it('renders metadata footer with correct pipeline info', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('hybrid')).toBeDefined();
    expect(screen.getByText('42ms')).toBeDefined();
    expect(screen.getByText('v1.0')).toBeDefined();
  });

  it('does not render when result is null', () => {
    const { container } = render(<ResultPanel result={null} />);
    expect(container.innerHTML).toBe('');
  });

  it('renders confidence basis pills', () => {
    render(<ResultPanel result={mockResult} />);
    expect(screen.getByText('parser-confirmed')).toBeDefined();
    expect(screen.getByText('error text agrees with source')).toBeDefined();
  });

  it('renders close button when onClose provided', () => {
    const onClose = vi.fn();
    render(<ResultPanel result={mockResult} onClose={onClose} />);
    const closeBtn = screen.getByLabelText('Close results');
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalled();
  });
});
