from typing import Any, Dict, List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.retrieval.base import BaseRetriever
from app.core.logging import logger


class SemanticRetriever(BaseRetriever):
    """Semantic search using Sentence Transformers and persistent document embeddings."""

    def __init__(
        self,
        documents: List[Dict[str, str]],
        model: SentenceTransformer,
        document_embeddings: np.ndarray
    ):
        self.documents = documents
        self.doc_map = {doc["id"]: doc for doc in documents}
        self.model = model
        self.document_embeddings = document_embeddings

        if self.document_embeddings.ndim != 2 or self.document_embeddings.shape[0] != len(documents):
            raise ValueError("Document embeddings array shape does not match corpus size.")

    @property
    def name(self) -> str:
        return "semantic"

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top-k documents by cosine similarity."""
        if not query or not query.strip():
            return []

        top_k = min(max(1, top_k), len(self.documents))

        # Encode query to normalized 1D embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]

        # Compute cosine similarity via dot product against pre-normalized document embeddings
        scores = self.document_embeddings @ query_embedding

        # Sort indices with deterministic tie-breaking (-score, doc_id)
        candidates = [
            (float(scores[idx]), self.documents[idx]["id"], idx)
            for idx in range(len(self.documents))
        ]
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
