import React, { useState, useEffect } from 'react';
import { getAnalyticsSummary } from '../services/api';

/**
 * Analytics view component rendering metric cards and clean SVG/CSS bars without external chart libraries.
 */
export function AnalyticsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const summary = await getAnalyticsSummary();
      setData(summary);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner"></div>
        <span>Loading analytics metrics...</span>
      </div>
    );
  }

  if (!data) {
    return <div className="analytics-empty">Failed to load analytics data.</div>;
  }

  const { total, by_error_type = {}, by_language = {}, by_severity = {}, by_ai_status = {}, daily_counts = [] } = data;

  const maxDaily = Math.max(...daily_counts.map(d => d.count), 1);

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <h2 className="page-heading">Diagnostic Analytics Summary</h2>
        <p className="page-subheading">Aggregated insight into error occurrences, languages, and pipeline resolution modes.</p>
      </div>

      {/* Top metrics cards */}
      <div className="metric-cards-grid">
        <div className="metric-card">
          <span className="metric-label">Total Analyses Run</span>
          <span className="metric-value">{total}</span>
          <span className="metric-sub">Across all supported languages</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Top Error Category</span>
          <span className="metric-value">
            {Object.entries(by_error_type)[0]?.[0] || 'N/A'}
          </span>
          <span className="metric-sub">{Object.entries(by_error_type)[0]?.[1] || 0} occurrences</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Primary Language</span>
          <span className="metric-value">
            {Object.entries(by_language)[0]?.[0] || 'N/A'}
          </span>
          <span className="metric-sub">{Object.entries(by_language)[0]?.[1] || 0} requests</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">AI Full Success Rate</span>
          <span className="metric-value">
            {total ? `${Math.round(((by_ai_status.ok || 0) / total) * 100)}%` : '0%'}
          </span>
          <span className="metric-sub">{by_ai_status.ok || 0} full hybrid diagnoses</span>
        </div>
      </div>

      {/* Daily trend bar chart (SVG) */}
      <div className="analytics-section chart-section">
        <h3 className="section-title">Daily Activity Trend (Recent Days)</h3>
        <div className="svg-chart-container">
          <svg className="bar-chart-svg" viewBox="0 0 500 160" preserveAspectRatio="none">
            {daily_counts.map((day, idx) => {
              const barWidth = 40;
              const gap = 60;
              const x = 50 + idx * gap;
              const barHeight = (day.count / maxDaily) * 100;
              const y = 130 - barHeight;

              return (
                <g key={day.date} className="bar-group">
                  <rect
                    x={x}
                    y={y}
                    width={barWidth}
                    height={barHeight}
                    rx="4"
                    className="chart-bar"
                  />
                  <text x={x + barWidth / 2} y={y - 8} textAnchor="middle" className="bar-value-text">
                    {day.count}
                  </text>
                  <text x={x + barWidth / 2} y={150} textAnchor="middle" className="bar-label-text">
                    {day.date.slice(5)}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Breakdown distributions */}
      <div className="distributions-grid">
        <div className="analytics-card">
          <h4 className="card-title">Distribution by Category</h4>
          <ul className="bar-list">
            {Object.entries(by_error_type).map(([cat, count]) => {
              const pct = total ? Math.round((count / total) * 100) : 0;
              return (
                <li key={cat} className="bar-list-item">
                  <div className="bar-item-info">
                    <span className="bar-name">{cat}</span>
                    <span className="bar-count">{count} ({pct}%)</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${pct}%` }}></div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="analytics-card">
          <h4 className="card-title">Distribution by Language</h4>
          <ul className="bar-list">
            {Object.entries(by_language).map(([lang, count]) => {
              const pct = total ? Math.round((count / total) * 100) : 0;
              return (
                <li key={lang} className="bar-list-item">
                  <div className="bar-item-info">
                    <span className="bar-name">{lang}</span>
                    <span className="bar-count">{count} ({pct}%)</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill bar-fill-lang" style={{ width: `${pct}%` }}></div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="analytics-card">
          <h4 className="card-title">Distribution by Severity</h4>
          <ul className="bar-list">
            {Object.entries(by_severity).map(([sev, count]) => {
              const pct = total ? Math.round((count / total) * 100) : 0;
              return (
                <li key={sev} className="bar-list-item">
                  <div className="bar-item-info">
                    <span className="bar-name">{sev}</span>
                    <span className="bar-count">{count} ({pct}%)</span>
                  </div>
                  <div className="bar-track">
                    <div className={`bar-fill bar-fill-sev-${sev.toLowerCase()}`} style={{ width: `${pct}%` }}></div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
