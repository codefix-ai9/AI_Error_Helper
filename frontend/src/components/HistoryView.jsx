import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/api';

/**
 * History view component implementing debounced search, filters, view, and delete.
 * @param {{ onSelectResult: (res: Object) => void }} props
 */
export function HistoryView({ onSelectResult }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedLang, setSelectedLang] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);

  // 300ms debounce on search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  useEffect(() => {
    loadData();
  }, [debouncedSearch, selectedLang, selectedType, selectedSeverity]);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getHistory({
        q: debouncedSearch,
        language: selectedLang,
        error_type: selectedType,
        severity: selectedSeverity
      });
      setHistoryItems(data?.items || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this analysis record?')) {
      setHistoryItems(prev => prev.filter(item => item.analysis_id !== id));
    }
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <h2 className="page-heading">Analysis History</h2>
        <p className="page-subheading">View, filter, or reload previous deterministic and AI-assisted diagnoses.</p>
      </div>

      <div className="history-filters-bar">
        <div className="filter-input-wrap">
          <input
            type="search"
            className="filter-search-input"
            placeholder="Search by summary, error, or language..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <select
          className="filter-select"
          value={selectedLang}
          onChange={(e) => setSelectedLang(e.target.value)}
          aria-label="Filter by language"
        >
          <option value="">All Languages</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
        </select>

        <select
          className="filter-select"
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          aria-label="Filter by error type"
        >
          <option value="">All Categories</option>
          <option value="Name / Reference">Name / Reference</option>
          <option value="Type">Type</option>
          <option value="Syntax">Syntax</option>
          <option value="Runtime">Runtime</option>
        </select>

        <select
          className="filter-select"
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          aria-label="Filter by severity"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
      </div>

      {loading ? (
        <div className="history-loading">
          <div className="spinner"></div>
          <span>Loading historical analyses...</span>
        </div>
      ) : historyItems.length === 0 ? (
        <div className="history-empty">
          <p>No analysis records match your search criteria.</p>
        </div>
      ) : (
        <div className="history-table-container">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Language</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Summary</th>
                <th>AI Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {historyItems.map((item) => (
                <tr
                  key={item.analysis_id}
                  className="history-row"
                  onClick={() => onSelectResult(item)}
                  title="Click to view full diagnosis"
                >
                  <td className="cell-date">
                    {new Date(item.created_at || Date.now()).toLocaleDateString()}
                  </td>
                  <td>
                    <span className="lang-tag">{item.language}</span>
                  </td>
                  <td>
                    <strong>{item.error_type}</strong>
                  </td>
                  <td>
                    <span className={`sev-tag sev-${(item.severity || 'unknown').toLowerCase()}`}>
                      {item.severity}
                    </span>
                  </td>
                  <td className="cell-summary" title={item.summary}>
                    {item.summary}
                  </td>
                  <td>
                    <span className={`status-pill status-${item.ai_status}`}>
                      {item.ai_status}
                    </span>
                  </td>
                  <td className="cell-actions">
                    <button
                      type="button"
                      className="btn-view"
                      onClick={() => onSelectResult(item)}
                    >
                      View
                    </button>
                    <button
                      type="button"
                      className="btn-delete"
                      onClick={(e) => handleDelete(item.analysis_id, e)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
