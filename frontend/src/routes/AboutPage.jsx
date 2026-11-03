import React from 'react';
import AppLayout from '../components/layout/AppLayout';
import { Database, Cpu, Layers, ShieldAlert, Award, FileCode } from 'lucide-react';

export default function AboutPage() {
  return (
    <AppLayout
      title="About MediRetrieve & Methodology"
      description="Academic Information Retrieval benchmark and system architecture for NFCorpus."
    >
      <div className="about-hero">
        <h2>MediRetrieve Project Overview</h2>
        <p>
          MediRetrieve is an academic Information Retrieval (IR) application built on the <strong>NFCorpus dataset</strong> (a medical retrieval benchmark from the BeIR suite). 
          The project investigates how traditional keyword search, probabilistic lexical models, dense vector embeddings, and rank fusion compare in medical document search.
        </p>
      </div>

      <div className="about-grid">
        <div className="about-card">
          <h3><Database size={18} color="var(--primary)" /> NFCorpus Dataset</h3>
          <p>
            NFCorpus contains 3,633 medical articles from PubMed and PubMed Central, paired with natural language queries and 3-level relevance judgments (0 = non-relevant, 1 = marginally relevant, 2 = highly relevant).
          </p>
        </div>

        <div className="about-card">
          <h3><Cpu size={18} color="var(--teal)" /> TF-IDF Vector Space Model</h3>
          <p>
            Unigram and bigram TF-IDF vectorizer fitted on the corpus. Uses sublinear term frequency scaling and cosine similarity over sparse document-term matrices.
          </p>
        </div>

        <div className="about-card">
          <h3><Layers size={18} color="var(--violet)" /> BM25 Okapi & spaCy</h3>
          <p>
            Probabilistic lexical retrieval using spaCy lemmatization. Customized to preserve medical negation terms (e.g. <em>no</em>, <em>not</em>, <em>without</em>, <em>lack</em>) during tokenization.
          </p>
        </div>

        <div className="about-card">
          <h3><Award size={18} color="var(--amber)" /> Semantic Search & Hybrid RRF</h3>
          <p>
            Dense embeddings from <code>sentence-transformers/all-MiniLM-L6-v2</code>. Hybrid RRF combines rank positions using $RRF(d) = \sum \frac{1}{k + rank_i(d)}$ with $k=60$.
          </p>
        </div>
      </div>

      <div className="methodology-box">
        <h3><ShieldAlert size={18} inline style={{ marginRight: '0.5rem', color: 'var(--amber)' }} /> Academic Disclaimer</h3>
        <p>
          This application is strictly an Information Retrieval academic research prototype designed to benchmark search algorithms. 
          It is <strong>not</strong> a clinical decision support tool and must not be used for diagnosis, medical advice, or treatment planning.
        </p>
      </div>
    </AppLayout>
  );
}
