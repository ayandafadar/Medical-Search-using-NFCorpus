import React, { useState } from 'react';
import { Search, X, Sparkles, Layers, Sliders } from 'lucide-react';

const EXAMPLE_QUERIES = [
  "What are the health benefits of omega-3 fatty acids?",
  "Vitamin D deficiency and bone health",
  "Effects of diet on cardiovascular disease",
  "Does fish oil improve heart health?",
  "Statin use in breast cancer survival"
];

const MODELS = [
  { id: 'rrf', name: 'Hybrid RRF', badge: 'Recommended', desc: 'Reciprocal Rank Fusion of TF-IDF, BM25, and Semantic Search' },
  { id: 'semantic', name: 'Semantic Search', badge: 'Neural', desc: 'Sentence Transformer (MiniLM-L6-v2) embeddings' },
  { id: 'bm25', name: 'BM25 Okapi', badge: 'Lexical', desc: 'Probabilistic keyword search with negation preservation' },
  { id: 'tfidf', name: 'TF-IDF', badge: 'Keyword', desc: 'Classic vector space model with n-gram term weighting' }
];

export default function SearchForm({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('rrf');
  const [topK, setTopK] = useState(10);
  const [enableExpansion, setEnableExpansion] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSearch({
      query: query.trim(),
      model: selectedModel,
      top_k: topK,
      enable_expansion: enableExpansion
    });
  };

  const handleExampleClick = (example) => {
    setQuery(example);
    onSearch({
      query: example,
      model: selectedModel,
      top_k: topK,
      enable_expansion: enableExpansion
    });
  };

  return (
    <div className="search-card">
      <form onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <Search size={20} className="search-input-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Enter a medical query (e.g. omega-3 benefits, hypertension treatments)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
          {query && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => setQuery('')}
              aria-label="Clear query"
            >
              <X size={18} />
            </button>
          )}
          <button
            type="submit"
            className="search-submit-btn"
            disabled={!query.trim() || isLoading}
          >
            <Search size={16} />
            <span>{isLoading ? 'Searching...' : 'Search'}</span>
          </button>
        </div>

        <div className="search-controls-row">
          <div className="model-selector-group">
            {MODELS.map((model) => (
              <button
                key={model.id}
                type="button"
                className={`model-pill ${model.id} ${selectedModel === model.id ? 'active' : ''}`}
                onClick={() => setSelectedModel(model.id)}
                title={model.desc}
              >
                <span>{model.name}</span>
                {model.id === 'rrf' && <Sparkles size={12} />}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <div className="topk-selector-group">
              <Sliders size={14} />
              <span>Results:</span>
              <select
                className="topk-select"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            <label className="expansion-toggle">
              <input
                type="checkbox"
                checked={enableExpansion}
                onChange={(e) => setEnableExpansion(e.target.checked)}
              />
              <span>Medical Synonym Expansion</span>
            </label>
          </div>
        </div>
      </form>

      <div className="example-chips-row">
        <span className="example-chip-label">Try Examples:</span>
        {EXAMPLE_QUERIES.map((example, idx) => (
          <button
            key={idx}
            type="button"
            className="example-chip"
            onClick={() => handleExampleClick(example)}
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
