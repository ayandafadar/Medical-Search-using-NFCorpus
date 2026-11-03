import React from 'react';
import { Award, Info } from 'lucide-react';

const MODEL_DESCRIPTIONS = {
  tfidf: 'Classic term-frequency vector space model with n-grams',
  bm25: 'Probabilistic Okapi BM25 with spaCy lemmatization & negation preservation',
  semantic: 'Dense neural retrieval using sentence-transformers/all-MiniLM-L6-v2',
  rrf: 'Hybrid Reciprocal Rank Fusion of TF-IDF, BM25, and Semantic Search'
};

const MODEL_LABELS = {
  tfidf: 'TF-IDF',
  bm25: 'BM25 Okapi',
  semantic: 'Semantic Search',
  rrf: 'Hybrid RRF'
};

export default function MetricsTable({ resultsData }) {
  if (!resultsData || !resultsData.results) {
    return null;
  }

  const { split, evaluated_queries, metric_k, results } = resultsData;

  const models = Object.keys(results);

  // Compute maximum value for each column metric across all models
  const maxValues = {
    p: Math.max(...models.map(m => results[m][`Precision@${metric_k}`] || 0)),
    r: Math.max(...models.map(m => results[m][`Recall@${metric_k}`] || 0)),
    map: Math.max(...models.map(m => results[m]['MAP'] || 0)),
    ndcg: Math.max(...models.map(m => results[m][`nDCG@${metric_k}`] || 0)),
  };

  return (
    <div className="table-card">
      <div className="table-header-bar">
        <h3>Retrieval Models Performance Comparison</h3>
        <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
          Dataset Split: <strong style={{ textTransform: 'uppercase' }}>{split}</strong> | <strong>{evaluated_queries}</strong> Evaluated Queries
        </div>
      </div>

      <div className="table-container">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Model Name</th>
              <th>Type / Algorithm</th>
              <th style={{ textAlign: 'right' }}>Precision@{metric_k}</th>
              <th style={{ textAlign: 'right' }}>Recall@{metric_k}</th>
              <th style={{ textAlign: 'right' }}>MAP</th>
              <th style={{ textAlign: 'right' }}>nDCG@{metric_k}</th>
            </tr>
          </thead>
          <tbody>
            {models.map((modelKey) => {
              const metrics = results[modelKey];
              const pVal = metrics[`Precision@${metric_k}`] || 0;
              const rVal = metrics[`Recall@${metric_k}`] || 0;
              const mapVal = metrics['MAP'] || 0;
              const ndcgVal = metrics[`nDCG@${metric_k}`] || 0;

              const isBestP = Math.abs(pVal - maxValues.p) < 1e-5;
              const isBestR = Math.abs(rVal - maxValues.r) < 1e-5;
              const isBestMap = Math.abs(mapVal - maxValues.map) < 1e-5;
              const isBestNdcg = Math.abs(ndcgVal - maxValues.ndcg) < 1e-5;

              return (
                <tr key={modelKey}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className={`model-badge-inline ${modelKey}`}>
                        {MODEL_LABELS[modelKey] || modelKey.toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {MODEL_DESCRIPTIONS[modelKey]}
                  </td>
                  <td className="table-cell-metric">
                    {isBestP ? (
                      <span className="cell-winner">{pVal.toFixed(4)}</span>
                    ) : (
                      pVal.toFixed(4)
                    )}
                  </td>
                  <td className="table-cell-metric">
                    {isBestR ? (
                      <span className="cell-winner">{rVal.toFixed(4)}</span>
                    ) : (
                      rVal.toFixed(4)
                    )}
                  </td>
                  <td className="table-cell-metric">
                    {isBestMap ? (
                      <span className="cell-winner">{mapVal.toFixed(4)}</span>
                    ) : (
                      mapVal.toFixed(4)
                    )}
                  </td>
                  <td className="table-cell-metric">
                    {isBestNdcg ? (
                      <span className="cell-winner">{ndcgVal.toFixed(4)}</span>
                    ) : (
                      ndcgVal.toFixed(4)
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
