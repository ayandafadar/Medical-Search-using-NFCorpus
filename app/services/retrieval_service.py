from typing import Any, Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import Settings
from app.core.exceptions import (
    InvalidQueryError,
    RetrievalInitializationError,
    ServiceNotReadyError,
)
from app.core.logging import logger
from app.retrieval.base import BaseRetriever
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.rrf import HybridRRFRetriever
from app.retrieval.semantic import SemanticRetriever
from app.retrieval.tfidf import TFIDFRetriever
from app.services.cache_service import CacheService
from app.services.corpus_service import CorpusService
from app.services.expansion_service import MedicalExpansionService


class RetrievalService:
    """
    Central orchestration service holding single in-memory instances of all retrieval models,
    indexes, corpus data, and expansion services.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.corpus_service = CorpusService(settings.corpus_path)
        self.cache_service = CacheService(
            settings.embeddings_path, settings.metadata_path
        )
        self.expansion_service = MedicalExpansionService(
            enabled=settings.ENABLE_MEDICAL_EXPANSION
        )

        self.st_model: Optional[SentenceTransformer] = None
        self.document_embeddings: Optional[np.ndarray] = None

        self.retrievers: Dict[str, BaseRetriever] = {}
        self.ready: bool = False
        self.cache_status: str = "uninitialized"

    def initialize(self) -> None:
        """
        Load corpus, initialize TF-IDF, BM25, load/encode semantic embeddings once,
        build RRF hybrid retriever, and mark service ready.
        """
        logger.info("Initializing RetrievalService...")

        try:
            # 1. Load and validate corpus
            documents = self.corpus_service.load()
            fingerprint = self.corpus_service.fingerprint

            # 2. Initialize TF-IDF retriever
            logger.info("Initializing TF-IDF engine...")
            tfidf_engine = TFIDFRetriever(documents)
            self.retrievers["tfidf"] = tfidf_engine

            # 3. Initialize BM25 retriever
            logger.info("Initializing BM25 engine with spaCy...")
            bm25_engine = BM25Retriever(documents, spacy_model=self.settings.SPACY_MODEL)
            self.retrievers["bm25"] = bm25_engine

            # 4. Load Sentence Transformer model
            logger.info(f"Loading Sentence Transformer model '{self.settings.MODEL_NAME}'...")
            self.st_model = SentenceTransformer(self.settings.MODEL_NAME)
            embedding_dim = (
                self.st_model.get_embedding_dimension()
                if hasattr(self.st_model, "get_embedding_dimension")
                else self.st_model.get_sentence_embedding_dimension()
            )

            # 5. Load or generate persistent document embeddings
            embeddings = self.cache_service.load_valid_embeddings(
                documents=documents,
                expected_model_name=self.settings.MODEL_NAME,
                expected_dim=embedding_dim,
                corpus_fingerprint=fingerprint
            )

            if embeddings is not None:
                self.document_embeddings = embeddings
                self.cache_status = "loaded_from_cache"
            else:
                logger.info("Generating corpus document embeddings...")
                contents = [doc["content"] for doc in documents]
                self.document_embeddings = self.st_model.encode(
                    contents,
                    batch_size=32,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                self.cache_service.save_embeddings(
                    embeddings=self.document_embeddings,
                    documents=documents,
                    model_name=self.settings.MODEL_NAME,
                    embedding_dim=embedding_dim,
                    corpus_fingerprint=fingerprint
                )
                self.cache_status = "rebuilt_and_cached"

            # 6. Initialize Semantic retriever
            logger.info("Initializing Semantic engine...")
            semantic_engine = SemanticRetriever(
                documents=documents,
                model=self.st_model,
                document_embeddings=self.document_embeddings
            )
            self.retrievers["semantic"] = semantic_engine

            # 7. Initialize Hybrid RRF retriever
            logger.info("Initializing Hybrid RRF engine...")
            rrf_engine = HybridRRFRetriever(
                documents=documents,
                tfidf_retriever=tfidf_engine,
                bm25_retriever=bm25_engine,
                semantic_retriever=semantic_engine,
                rrf_k=self.settings.RRF_K,
                candidate_k=self.settings.RRF_CANDIDATE_K
            )
            self.retrievers["rrf"] = rrf_engine

            self.ready = True
            logger.info("RetrievalService successfully initialized and marked READY.")

        except Exception as e:
            self.ready = False
            logger.error(f"RetrievalService initialization failed: {str(e)}")
            raise RetrievalInitializationError(f"Failed to initialize retrieval service: {str(e)}") from e

    def close(self) -> None:
        """Cleanup resources on application shutdown."""
        logger.info("Closing RetrievalService resources.")
        self.ready = False

    def search(
        self,
        query: str,
        model_name: str = "rrf",
        top_k: int = 10,
        enable_expansion: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute search request against the initialized specified retriever.
        """
        if not self.ready:
            raise ServiceNotReadyError("Retrieval service is not ready to serve requests.")

        model_key = model_name.lower().strip()
        if model_key not in self.retrievers:
            raise InvalidQueryError(
                f"Unknown retrieval model '{model_name}'. Available: {list(self.retrievers.keys())}"
            )

        # Decide expansion usage
        use_expansion = (
            enable_expansion
            if enable_expansion is not None
            else self.expansion_service.enabled
        )

        expanded_query = None
        search_query = query
        if use_expansion:
            temp_expansion_service = MedicalExpansionService(enabled=True)
            expanded_query = temp_expansion_service.expand_query(query)
            search_query = expanded_query

        engine = self.retrievers[model_key]
        results = engine.search(search_query, top_k=top_k)

        return {
            "query": query,
            "expanded_query": expanded_query if expanded_query != query else None,
            "model": model_key,
            "count": len(results),
            "results": results,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get structured status for health endpoint."""
        retrievers_status = {name: (engine is not None) for name, engine in self.retrievers.items()}
        return {
            "status": "healthy" if self.ready else "unhealthy",
            "initialized": self.ready,
            "retrievers": retrievers_status,
            "cache_status": self.cache_status,
            "document_count": self.corpus_service.document_count if self.ready else 0,
        }
