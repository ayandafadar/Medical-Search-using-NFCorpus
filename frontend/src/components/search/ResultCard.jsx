import React, { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp, FileText, Tag } from 'lucide-react';

export default function ResultCard({ result, rank, modelName }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleCopyId = () => {
    navigator.clipboard.writeText(result.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isRRF = modelName === 'rrf';
  const isSemantic = modelName === 'semantic';
  const isBM25 = modelName === 'bm25';

  const scoreLabel = isRRF
    ? `RRF Score: ${result.score.toFixed(6)}`
    : isSemantic
    ? `Cosine Similarity: ${result.score.toFixed(4)}`
    : `Score: ${result.score.toFixed(4)}`;

  const previewText = expanded
    ? result.text
    : result.text.length > 320
    ? `${result.text.slice(0, 320)}...`
    : result.text;

  return (
    <div className="result-card">
      <div className="result-card-header">
        <div className="result-title-group">
          <div className={`result-rank-badge ${rank === 1 ? 'top-1' : ''}`}>
            #{rank}
          </div>
          <h4 className="result-title">{result.title || 'Untitled Medical Document'}</h4>
        </div>

        <div className={`score-badge ${modelName}`}>
          {scoreLabel}
        </div>
      </div>

      <div className="result-meta-row">
        <span>Doc ID:</span>
        <span className="doc-id-tag">{result.id}</span>
        <button
          className="search-clear-btn"
          onClick={handleCopyId}
          title="Copy Document ID"
          style={{ position: 'static', padding: '0.15rem 0.35rem' }}
        >
          {copied ? <Check size={14} color="var(--success)" /> : <Copy size={14} />}
        </button>
      </div>

      {result.matched_terms && result.matched_terms.length > 0 && (
        <div className="matched-terms-row">
          <Tag size={13} />
          <span>Matched Terms:</span>
          {result.matched_terms.map((term, idx) => (
            <span key={idx} className="matched-term-tag">{term}</span>
          ))}
        </div>
      )}

      {result.component_ranks && (
        <div className="component-ranks-row">
          <span>Component Ranks:</span>
          {Object.entries(result.component_ranks).map(([key, val]) => (
            <span key={key} className="component-rank-tag">
              {key.toUpperCase()}: <strong>#{val}</strong>
            </span>
          ))}
        </div>
      )}

      <p className="result-text">{previewText}</p>

      {result.text.length > 320 && (
        <button
          className="result-expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <>
              <span>Show Less</span>
              <ChevronUp size={14} />
            </>
          ) : (
            <>
              <span>Show Full Text</span>
              <ChevronDown size={14} />
            </>
          )}
        </button>
      )}
    </div>
  );
}
