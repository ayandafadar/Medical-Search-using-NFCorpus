import React, { useState, useEffect } from 'react';
import AppLayout from '../components/layout/AppLayout';
import MetricsTable from '../components/comparison/MetricsTable';
import MetricSummary from '../components/comparison/MetricSummary';
import { fetchEvaluationResults } from '../services/api';
import { BookOpen, RefreshCw } from 'lucide-react';

export default function ComparisonPage() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const loadResults = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetchEvaluationResults('test');
        if (isMounted) setData(res);
      } catch (err) {
        if (isMounted) setError(err.message || 'Failed to load evaluation results.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadResults();
    return () => { isMounted = false; };
  }, []);

  return (
    <AppLayout
      title="Performance Comparison"
      description="Empirical comparison of TF-IDF, BM25, Semantic Search, and Hybrid RRF on NFCorpus relevance judgments."
    >
      {error && (
        <div className="error-banner">
          <span>Failed to load evaluation metrics: {error}</span>
        </div>
      )}

      {isLoading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading evaluation metrics...
        </div>
      ) : (
        <>
          <MetricSummary resultsData={data} />
          <MetricsTable resultsData={data} />

          <div className="methodology-box">
            <h3><BookOpen size={18} inline style={{ marginRight: '0.5rem' }} /> Evaluation Benchmark Methodology</h3>
            <p>
              Evaluation is performed on the official <strong>NFCorpus test split</strong> (323 queries and 3,633 medical documents). 
              Every model retrieves candidate documents for the exact same query set. Rankings are evaluated against ground-truth human relevance judgments.
            </p>

            <div className="metric-definition-grid">
              <div className="metric-def-item">
                <h4>Precision@10</h4>
                <p>The fraction of top-10 retrieved documents that are relevant (rel &ge; 1).</p>
              </div>

              <div className="metric-def-item">
                <h4>Recall@10</h4>
                <p>The fraction of all relevant documents for a query that appear in the top 10 results.</p>
              </div>

              <div className="metric-def-item">
                <h4>Mean Average Precision (MAP)</h4>
                <p>The mean of Average Precision across all queries, penalizing relevant items retrieved at lower ranks.</p>
              </div>

              <div className="metric-def-item">
                <h4>nDCG@10</h4>
                <p>Normalized Discounted Cumulative Gain at rank 10 using 3-level graded relevance (0=non-relevant, 1=marginal, 2=high).</p>
              </div>
            </div>
          </div>
        </>
      )}
    </AppLayout>
  );
}
