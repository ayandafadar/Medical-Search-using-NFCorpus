import React, { useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import SearchForm from '../components/search/SearchForm';
import ResultList from '../components/search/ResultList';
import { executeSearch } from '../services/api';

export default function SearchPage() {
  const [searchResponse, setSearchResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (payload) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await executeSearch(payload);
      setSearchResponse(data);
    } catch (err) {
      setError(err.message || 'Failed to execute search query against backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout
      title="Medical Literature Search"
      description="Query 3,633 medical documents from the NFCorpus benchmark using TF-IDF, BM25, Semantic Search, or Hybrid RRF."
    >
      <SearchForm onSearch={handleSearch} isLoading={isLoading} />
      <ResultList
        searchResponse={searchResponse}
        isLoading={isLoading}
        error={error}
      />
    </AppLayout>
  );
}
