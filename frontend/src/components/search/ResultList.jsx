import React from 'react';
import ResultCard from './ResultCard';
import { Search, AlertCircle, FileQuestion, CheckCircle2 } from 'lucide-react';

export default function ResultList({ searchResponse, isLoading, error }) {
  if (error) {
    return (
      <div className="error-banner">
        <AlertCircle size={20} />
        <div>
          <strong>Search Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div>
        <div style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Executing retrieval & ranking...
        </div>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton skeleton-title"></div>
            <div className="skeleton skeleton-text"></div>
            <div className="skeleton skeleton-text" style={{ width: '70%' }}></div>
          </div>
        ))}
      </div>
    );
  }

  if (!searchResponse) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <Search size={28} />
        </div>
        <h3>Medical Literature Search</h3>
        <p>Enter a query above or click an example to retrieve ranked medical documents from the NFCorpus dataset.</p>
      </div>
    );
  }

  const { query, expanded_query, model, count, results } = searchResponse;

  if (!results || results.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <FileQuestion size={28} />
        </div>
        <h3>No Matching Documents Found</h3>
        <p>No documents in the NFCorpus dataset matched your query with the selected model. Try broadening your terms or using Medical Synonym Expansion.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="results-header">
        <div className="results-count">
          Showing <strong>{results.length}</strong> results for "<strong>{query}</strong>" using <strong>{model.toUpperCase()}</strong>
          {expanded_query && (
            <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Expanded Query: <em>{expanded_query}</em>
            </div>
          )}
        </div>
      </div>

      <div>
        {results.map((result, idx) => (
          <ResultCard
            key={result.id}
            result={result}
            rank={idx + 1}
            modelName={model}
          />
        ))}
      </div>
    </div>
  );
}
