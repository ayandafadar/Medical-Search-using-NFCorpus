from typing import Any, Dict, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.retrieval.base import BaseRetriever
from app.core.logging import logger


class TFIDFRetriever(BaseRetriever):
    """Keyword-based medical document retrieval system using TF-IDF."""

    def __init__(self, documents: List[Dict[str, str]]):
        self.documents = documents
        self.doc_map = {doc["id"]: doc for doc in documents}

        logger.info("Fitting TF-IDF vectorizer on document corpus...")
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        # Build sparse document-term matrix
        contents = [doc["content"] for doc in documents]
        self.document_matrix = self.vectorizer.fit_transform(contents)
        logger.info("TF-IDF vectorizer ready.")

    @property
    def name(self) -> str:
        return "tfidf"

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Return top-k documents ranked by TF-IDF cosine similarity."""
        if not query or not query.strip():
            return []

        top_k = min(max(1, top_k), len(self.documents))
        query_vector = self.vectorizer.transform([query])

        # Compute cosine similarity against sparse document matrix
        scores = cosine_similarity(query_vector, self.document_matrix).ravel()

        # Filter out non-matching documents (score <= 0)
        valid_indices = np.where(scores > 0)[0]
        if len(valid_indices) == 0:
            return []

        # Sort by (-score, doc_id) for deterministic tie-breaking
        candidates = []
        for idx in valid_indices:
            candidates.append((float(scores[idx]), self.documents[idx]["id"], idx))

        candidates.sort(key=lambda x: (-x[0], x[1]))

        results = []
        for score, doc_id, idx in candidates[:top_k]:
            doc = self.documents[idx]
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "score": score,
                "retriever": self.name
            })

        return results
