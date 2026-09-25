import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

describe('App Component and Workflow', () => {
  it('renders header, inputs, and run analysis button', () => {
    render(<App />);

    expect(screen.getByText(/AI Programming Error Helper/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Source Code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Compiler \/ Runtime Error/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Hybrid Analysis/i })).toBeInTheDocument();
  });

  it('displays client validation messages when submitted with empty fields', async () => {
    render(<App />);

    const runBtn = screen.getByRole('button', { name: /Run Hybrid Analysis/i });
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(screen.getByText('Please provide the source code before analysis.')).toBeInTheDocument();
      expect(screen.getByText('Please provide the compiler/runtime error or observed problem.')).toBeInTheDocument();
    });
  });

  it('runs analysis in fixture mode and displays ResultPanel with static findings and AI explanation', async () => {
    render(<App />);

    // Fill source code and error
    const sourceTextarea = screen.getByPlaceholderText(/\/\/ Paste or write your source code here/i);
    const errorTextarea = screen.getByPlaceholderText(/Paste your compiler traceback/i);

    fireEvent.change(sourceTextarea, { target: { value: 'print(total)' } });
    fireEvent.change(errorTextarea, { target: { value: 'NameError: name total is not defined' } });

    const runBtn = screen.getByRole('button', { name: /Run Hybrid Analysis/i });
    fireEvent.click(runBtn);

    // Expect loading state
    expect(screen.getByText(/Analyzing Diagnostics/i)).toBeInTheDocument();

    // Wait for analysis result to appear
    await waitFor(() => {
      expect(screen.getByText(/Diagnostic & Educational Result/i)).toBeInTheDocument();
      expect(screen.getByText(/Name \/ Reference/i)).toBeInTheDocument();
      expect(screen.getByText(/Detected by Static Analysis/i)).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /Educational Explanation/i })).toBeInTheDocument();
    }, { timeout: 4000 });
  });

  it('navigates to History and Analytics tabs', async () => {
    render(<App />);

    const historyTab = screen.getByRole('button', { name: /History/i });
    fireEvent.click(historyTab);
    expect(screen.getByText(/Analysis History/i)).toBeInTheDocument();

    const analyticsTab = screen.getByRole('button', { name: /Analytics/i });
    fireEvent.click(analyticsTab);
    await waitFor(() => {
      expect(screen.getByText(/Diagnostic Analytics Summary/i)).toBeInTheDocument();
    });
  });
});
