import React from 'react';
import { Award, Target, TrendingUp, Layers } from 'lucide-react';

export default function MetricSummary({ resultsData }) {
  if (!resultsData || !resultsData.results) return null;

  const { results, metric_k, evaluated_queries } = resultsData;
  const models = Object.keys(results);

  let bestNdcg = { model: '', value: 0 };
  let bestMap = { model: '', value: 0 };

  models.forEach(m => {
    const ndcg = results[m][`nDCG@${metric_k}`] || 0;
    const map = results[m]['MAP'] || 0;
    if (ndcg > bestNdcg.value) bestNdcg = { model: m, value: ndcg };
    if (map > bestMap.value) bestMap = { model: m, value: map };
  });

  return (
    <div className="metrics-summary-grid">
      <div className="metric-kpi-card">
        <div className="kpi-icon-box primary">
          <Layers size={24} />
        </div>
        <div className="kpi-content">
          <span>Evaluated Queries</span>
          <h3>{evaluated_queries}</h3>
          <p>NFCorpus test relevance queries</p>
        </div>
      </div>

      <div className="metric-kpi-card">
        <div className="kpi-icon-box amber">
          <Award size={24} />
        </div>
        <div className="kpi-content">
          <span>Highest nDCG@{metric_k}</span>
          <h3>{bestNdcg.value.toFixed(4)}</h3>
          <p>Top Model: <strong>{bestNdcg.model.toUpperCase()}</strong></p>
        </div>
      </div>

      <div className="metric-kpi-card">
        <div className="kpi-icon-box teal">
          <TrendingUp size={24} />
        </div>
        <div className="kpi-content">
          <span>Best Mean Avg Precision</span>
          <h3>{bestMap.value.toFixed(4)}</h3>
          <p>Top Model: <strong>{bestMap.model.toUpperCase()}</strong></p>
        </div>
      </div>

      <div className="metric-kpi-card">
        <div className="kpi-icon-box violet">
          <Target size={24} />
        </div>
        <div className="kpi-content">
          <span>Compared Methods</span>
          <h3>4 Models</h3>
          <p>TF-IDF, BM25, Semantic, RRF</p>
        </div>
      </div>
    </div>
  );
}
