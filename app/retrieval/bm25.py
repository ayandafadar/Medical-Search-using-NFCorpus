from typing import Any, Dict, List, Set
import numpy as np
import spacy
from rank_bm25 import BM25Okapi
from app.retrieval.base import BaseRetriever
from app.core.exceptions import RetrievalInitializationError
from app.core.logging import logger

NEGATION_WORDS: Set[str] = {
    "no", "not", "neither", "never", "nor", "without", "lack", "cannot", "non"
}


class BM25Retriever(BaseRetriever):
    """Medical document retrieval using BM25 with spaCy lemmatization and negation preservation."""

    def __init__(self, documents: List[Dict[str, str]], spacy_model: str = "en_core_web_sm"):
        self.documents = documents
        self.doc_map = {doc["id"]: doc for doc in documents}

        logger.info(f"Loading spaCy NLP model '{spacy_model}'...")
        try:
            self.nlp = spacy.load(spacy_model, disable=["parser", "ner"])
        except OSError as e:
            raise RetrievalInitializationError(
                f"spaCy model '{spacy_model}' not found. Please run: python -m spacy download {spacy_model}"
            ) from e

        # Customize stop-words to preserve medical negation terms
        for word in NEGATION_WORDS:
            if word in self.nlp.vocab:
                self.nlp.vocab[word].is_stop = False

        logger.info("Lemmatizing and tokenizing document corpus in batches...")
        self.tokenized_documents: List[List[str]] = []
        document_texts = [doc["content"] for doc in documents]

        for doc_spacy in self.nlp.pipe(document_texts, batch_size=100):
            tokens = self._extract_lemmas(doc_spacy)
            self.tokenized_documents.append(tokens)

        logger.info("Building BM25 index...")
        self.bm25 = BM25Okapi(self.tokenized_documents)
        logger.info("BM25 index ready.")

    def _extract_lemmas(self, doc_spacy) -> List[str]:
        """Extract lemmas, keeping negation terms and filtering punctuation/spaces/stop-words."""
        tokens = []
        for token in doc_spacy:
            lemma = token.lemma_.lower().strip()
            if not lemma or token.is_punct or token.is_space:
                continue
            # Keep token if it's a negation word OR if it's not a stop word
            if lemma in NEGATION_WORDS or not token.is_stop:
                tokens.append(lemma)
        return tokens

    def preprocess_query(self, query: str) -> List[str]:
        """Tokenize and lemmatize search query using identical pipeline."""
        query_doc = self.nlp(query)
        return self._extract_lemmas(query_doc)

    @property
    def name(self) -> str:
        return "bm25"

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Return top-k documents ranked by BM25 score."""
        if not query or not query.strip():
            return []

        top_k = min(max(1, top_k), len(self.documents))
        query_tokens = self.preprocess_query(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        # Filter out documents with score <= 0
        valid_indices = np.where(scores > 0)[0]
        if len(valid_indices) == 0:
            return []

        candidates = []
        query_token_set = set(query_tokens)

        for idx in valid_indices:
            candidates.append((float(scores[idx]), self.documents[idx]["id"], idx))

        candidates.sort(key=lambda x: (-x[0], x[1]))

        results = []
        for score, doc_id, idx in candidates[:top_k]:
            doc = self.documents[idx]
            doc_tokens = self.tokenized_documents[idx]
            
            # Accurate document-specific matched terms
            matched_terms = sorted(list(query_token_set.intersection(set(doc_tokens))))

            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "score": score,
                "retriever": self.name,
                "matched_terms": matched_terms
            })

        return results
