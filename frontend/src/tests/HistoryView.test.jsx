import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HistoryView } from '../components/HistoryView';

// Mock the api module
vi.mock('../services/api', () => ({
  getHistory: vi.fn(),
  deleteHistoryItem: vi.fn(),
  USE_FIXTURES: false
}));

import { getHistory, deleteHistoryItem } from '../services/api';

describe('HistoryView', () => {
  const mockItems = [
    {
      analysis_id: 'test-id-1',
      created_at: '2026-09-20T10:00:00Z',
      language: 'python',
      error_type: 'Name / Reference',
      severity: 'HIGH',
      summary: 'Undefined variable total',
      ai_status: 'ok'
    },
    {
      analysis_id: 'test-id-2',
      created_at: '2026-09-21T12:00:00Z',
      language: 'javascript',
      error_type: 'Type',
      severity: 'MEDIUM',
      summary: 'Cannot read property of null',
      ai_status: 'mock'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    getHistory.mockResolvedValue({ items: mockItems, total: 2 });
    deleteHistoryItem.mockResolvedValue(true);
  });

  it('renders history items after loading', async () => {
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText('Undefined variable total')).toBeDefined();
      expect(screen.getByText('Cannot read property of null')).toBeDefined();
    });
  });

  it('shows empty state when no results', async () => {
    getHistory.mockResolvedValue({ items: [], total: 0 });
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText(/No analysis records/)).toBeDefined();
    });
  });

  it('passes filter params to API on language change', async () => {
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => {
      expect(getHistory).toHaveBeenCalled();
    });

    const langSelect = screen.getByLabelText('Filter by language');
    await act(async () => {
      fireEvent.change(langSelect, { target: { value: 'python' } });
    });
    await waitFor(() => {
      expect(getHistory).toHaveBeenCalledWith(
        expect.objectContaining({ language: 'python' })
      );
    });
  });

  it('passes severity filter to API', async () => {
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => expect(getHistory).toHaveBeenCalled());

    const sevSelect = screen.getByLabelText('Filter by severity');
    await act(async () => {
      fireEvent.change(sevSelect, { target: { value: 'HIGH' } });
    });
    await waitFor(() => {
      expect(getHistory).toHaveBeenCalledWith(
        expect.objectContaining({ severity: 'HIGH' })
      );
    });
  });

  it('calls onSelectResult when View button clicked', async () => {
    const onSelect = vi.fn();
    render(<HistoryView onSelectResult={onSelect} />);
    await waitFor(() => {
      expect(screen.getByText('Undefined variable total')).toBeDefined();
    });

    const viewButtons = screen.getAllByText('View');
    fireEvent.click(viewButtons[0]);
    expect(onSelect).toHaveBeenCalledWith(mockItems[0]);
  });

  it('delete-with-confirm calls API and removes item', async () => {
    window.confirm = vi.fn().mockReturnValue(true);
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText('Undefined variable total')).toBeDefined();
    });

    const deleteButtons = screen.getAllByText('Delete');
    await act(async () => {
      fireEvent.click(deleteButtons[0]);
    });
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteHistoryItem).toHaveBeenCalledWith('test-id-1');
  });

  it('cancelled delete does not call API', async () => {
    window.confirm = vi.fn().mockReturnValue(false);
    render(<HistoryView onSelectResult={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText('Undefined variable total')).toBeDefined();
    });

    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteHistoryItem).not.toHaveBeenCalled();
  });
});
