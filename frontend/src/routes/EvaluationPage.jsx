import React, { useState, useEffect } from 'react';
import AppLayout from '../components/layout/AppLayout';
import PrecisionRecallChart from '../components/evaluation/PrecisionRecallChart';
import { fetchEvaluationResults } from '../services/api';
import { LineChart, Info } from 'lucide-react';

export default function EvaluationPage() {
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
      title="Precision-Recall Analytics"
      description="Visualizing retrieval trade-offs across rank cutoffs k = 1 to 100 on NFCorpus test queries."
    >
      {error && (
        <div className="error-banner">
          <span>Failed to load precision-recall curves: {error}</span>
        </div>
      )}

      {isLoading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading precision-recall curves...
        </div>
      ) : (
        <>
          <PrecisionRecallChart evaluationData={data} />

          <div className="methodology-box">
            <h3><Info size={18} inline style={{ marginRight: '0.5rem' }} /> Interpreting Precision-Recall Curves</h3>
            <p>
              In Information Retrieval, a <strong>Precision-Recall curve</strong> illustrates the trade-off between precision (accuracy of retrieved results) and recall (completeness of retrieved relevant documents) across increasing rank cutoffs.
            </p>

            <div className="metric-definition-grid">
              <div className="metric-def-item">
                <h4>Curve Envelope & Area</h4>
                <p>A curve that sits higher and further to the right indicates superior overall retrieval performance across all cutoff thresholds.</p>
              </div>

              <div className="metric-def-item">
                <h4>Hybrid RRF Fusion</h4>
                <p>RRF combines reciprocal rank positions across lexical (BM25/TFIDF) and neural (Semantic) engines, maintaining higher precision even as recall expands.</p>
              </div>

              <div className="metric-def-item">
                <h4>Rank Cutoffs (k=1..100)</h4>
                <p>Data points represent mean precision and recall measured at cutoffs k &in; [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100].</p>
              </div>
            </div>
          </div>
        </>
      )}
    </AppLayout>
  );
}
