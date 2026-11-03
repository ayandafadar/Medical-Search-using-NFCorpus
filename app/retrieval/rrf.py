from collections import defaultdict
from typing import Any, Dict, List, Optional
from app.retrieval.base import BaseRetriever
from app.core.logging import logger


class HybridRRFRetriever(BaseRetriever):
    """Hybrid medical document retriever using Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        documents: List[Dict[str, str]],
        tfidf_retriever: BaseRetriever,
        bm25_retriever: BaseRetriever,
        semantic_retriever: BaseRetriever,
        rrf_k: int = 60,
        candidate_k: int = 100
    ):
        self.documents = documents
        self.doc_map = {doc["id"]: doc for doc in documents}

        self.tfidf = tfidf_retriever
        self.bm25 = bm25_retriever
        self.semantic = semantic_retriever

        self.rrf_k = rrf_k
        self.candidate_k = candidate_k

    @property
    def name(self) -> str:
        return "rrf"

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Fuse rankings from TF-IDF, BM25, and Semantic search engines."""
        if not query or not query.strip():
            return []

        top_k = min(max(1, top_k), len(self.documents))

        # Query all three retrievers with candidate depth candidate_k
        rankings: Dict[str, List[Dict[str, Any]]] = {
            "tfidf": self.tfidf.search(query, top_k=self.candidate_k),
            "bm25": self.bm25.search(query, top_k=self.candidate_k),
            "semantic": self.semantic.search(query, top_k=self.candidate_k),
        }

        fused_scores: Dict[str, float] = defaultdict(float)
        component_ranks: Dict[str, Dict[str, int]] = defaultdict(dict)
        component_scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Calculate reciprocal rank fusion score
        for system_name, results in rankings.items():
            for rank, result in enumerate(results, start=1):
                doc_id = result["id"]
                score_contrib = 1.0 / (self.rrf_k + rank)
                fused_scores[doc_id] += score_contrib
                component_ranks[doc_id][system_name] = rank
                component_scores[doc_id][system_name] = float(result.get("score", 0.0))

        if not fused_scores:
            return []

        # Deterministic sorting by (-rrf_score, doc_id)
        candidates = [
            (score, doc_id) for doc_id, score in fused_scores.items()
        ]
        candidates.sort(key=lambda x: (-x[0], x[1]))

        results = []
        for rrf_score, doc_id in candidates[:top_k]:
            doc = self.doc_map[doc_id]
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "score": rrf_score,
                "retriever": self.name,
                "component_ranks": dict(component_ranks[doc_id]),
                "component_scores": dict(component_scores[doc_id]),
            })

        return results
