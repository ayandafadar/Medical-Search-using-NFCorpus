import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './routes/SearchPage';
import ComparisonPage from './routes/ComparisonPage';
import EvaluationPage from './routes/EvaluationPage';
import AboutPage from './routes/AboutPage';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/comparison" element={<ComparisonPage />} />
        <Route path="/evaluation" element={<EvaluationPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </Router>
  );
}
