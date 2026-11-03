import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const MODEL_CONFIG = {
  rrf: { name: 'Hybrid RRF', color: '#D97706', strokeWidth: 3 },
  semantic: { name: 'Semantic Search', color: '#7C3AED', strokeWidth: 2 },
  bm25: { name: 'BM25 Okapi', color: '#0D9488', strokeWidth: 2 },
  tfidf: { name: 'TF-IDF', color: '#2563EB', strokeWidth: 2 },
};

export default function PrecisionRecallChart({ evaluationData }) {
  const [visibleModels, setVisibleModels] = useState({
    rrf: true,
    semantic: true,
    bm25: true,
    tfidf: true,
  });

  if (!evaluationData || !evaluationData.precision_recall) {
    return (
      <div className="empty-state">
        <h3>Precision-Recall Data Pending</h3>
        <p>Run the offline evaluation benchmark script to generate Precision-Recall curve data.</p>
      </div>
    );
  }

  const prCurves = evaluationData.precision_recall;
  const cutoffs = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100];

  // Combine model series into a single dataset array for Recharts
  const chartData = cutoffs.map((k, index) => {
    const item = { k };
    Object.keys(MODEL_CONFIG).forEach((modelKey) => {
      const points = prCurves[modelKey] || [];
      const pt = points.find((p) => p.k === k) || points[index];
      if (pt) {
        item[`${modelKey}_p`] = pt.precision;
        item[`${modelKey}_r`] = pt.recall;
      }
    });
    // Use average recall at this cutoff as X axis point
    const avgRecall =
      Object.keys(MODEL_CONFIG).reduce((sum, key) => sum + (item[`${key}_r`] || 0), 0) /
      Object.keys(MODEL_CONFIG).length;
    item.recall = Number(avgRecall.toFixed(4));
    return item;
  });

  // Sort by recall ascending for continuous left-to-right line chart
  chartData.sort((a, b) => a.recall - b.recall);

  const toggleModel = (modelKey) => {
    setVisibleModels((prev) => ({ ...prev, [modelKey]: !prev[modelKey] }));
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            padding: '0.85rem 1rem',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            fontSize: '0.825rem',
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: '0.4rem', color: '#0F172A' }}>
            Recall: {label}
          </div>
          {payload.map((entry, idx) => {
            const modelKey = entry.dataKey.replace('_p', '');
            const conf = MODEL_CONFIG[modelKey];
            const kVal = entry.payload.k;
            return (
              <div
                key={idx}
                style={{
                  color: entry.color,
                  marginBottom: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: entry.color,
                  }}
                />
                <strong>{conf?.name || modelKey}:</strong>
                <span>Precision = {entry.value?.toFixed(4)}</span>
                <span style={{ color: '#64748B', fontSize: '0.75rem' }}>(k={kVal})</span>
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <div className="chart-title-group">
          <h3>Precision-Recall Curves (NFCorpus Test Benchmark)</h3>
          <p>Interpolated Precision vs. Recall across rank cutoffs (k = 1 to 100)</p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {Object.entries(MODEL_CONFIG).map(([key, conf]) => (
            <button
              key={key}
              type="button"
              className={`model-pill ${key} ${visibleModels[key] ? 'active' : ''}`}
              onClick={() => toggleModel(key)}
              style={{
                borderColor: visibleModels[key] ? conf.color : '#E2E8F0',
                color: visibleModels[key] ? conf.color : '#64748B',
                opacity: visibleModels[key] ? 1 : 0.5,
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: conf.color,
                }}
              />
              <span>{conf.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="recall"
              type="number"
              domain={[0, 'auto']}
              tickFormatter={(v) => v.toFixed(2)}
              label={{ value: 'Recall', position: 'bottom', offset: 10, fill: '#475569', fontSize: 13 }}
            />
            <YAxis
              domain={[0, 'auto']}
              tickFormatter={(v) => v.toFixed(2)}
              label={{
                value: 'Precision',
                angle: -90,
                position: 'insideLeft',
                offset: 0,
                fill: '#475569',
                fontSize: 13,
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="top" height={36} />

            {visibleModels.rrf && (
              <Line
                type="monotone"
                dataKey="rrf_p"
                name="Hybrid RRF"
                stroke={MODEL_CONFIG.rrf.color}
                strokeWidth={MODEL_CONFIG.rrf.strokeWidth}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            )}
            {visibleModels.semantic && (
              <Line
                type="monotone"
                dataKey="semantic_p"
                name="Semantic Search"
                stroke={MODEL_CONFIG.semantic.color}
                strokeWidth={MODEL_CONFIG.semantic.strokeWidth}
                dot={{ r: 3 }}
              />
            )}
            {visibleModels.bm25 && (
              <Line
                type="monotone"
                dataKey="bm25_p"
                name="BM25 Okapi"
                stroke={MODEL_CONFIG.bm25.color}
                strokeWidth={MODEL_CONFIG.bm25.strokeWidth}
                dot={{ r: 3 }}
              />
            )}
            {visibleModels.tfidf && (
              <Line
                type="monotone"
                dataKey="tfidf_p"
                name="TF-IDF"
                stroke={MODEL_CONFIG.tfidf.color}
                strokeWidth={MODEL_CONFIG.tfidf.strokeWidth}
                dot={{ r: 3 }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
