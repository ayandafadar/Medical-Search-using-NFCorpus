import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from app.core.exceptions import CacheError
from app.core.logging import logger

CACHE_VERSION = "1.0"


class CacheService:
    """Service for validating, loading, and atomically writing persistent document embeddings."""

    def __init__(self, embeddings_path: Path, metadata_path: Path):
        self.embeddings_path = embeddings_path
        self.metadata_path = metadata_path

    def load_valid_embeddings(
        self,
        documents: List[Dict[str, str]],
        expected_model_name: str,
        expected_dim: int,
        corpus_fingerprint: str
    ) -> Optional[np.ndarray]:
        """
        Validate and load cached document embeddings.
        Returns numpy ndarray if valid, None if cache is missing, stale, or invalid.
        """
        if not self.embeddings_path.exists() or not self.metadata_path.exists():
            logger.info("Cache files missing. Embedding cache will be generated.")
            return None

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                raw_metadata = json.load(f)

            embeddings = np.load(self.embeddings_path, allow_pickle=False)

            # Check if metadata is in legacy format (list of dicts) or current format (dict)
            if isinstance(raw_metadata, list):
                logger.info("Found legacy cache metadata format. Checking document compatibility...")
                if len(raw_metadata) == len(documents):
                    cached_ids = [doc.get("id") for doc in raw_metadata]
                    doc_ids = [doc["id"] for doc in documents]
                    if cached_ids == doc_ids and embeddings.shape == (len(documents), expected_dim):
                        logger.info("Legacy cache verified! Upgrading metadata format...")
                        self.save_embeddings(
                            embeddings=embeddings,
                            documents=documents,
                            model_name=expected_model_name,
                            embedding_dim=expected_dim,
                            corpus_fingerprint=corpus_fingerprint
                        )
                        return embeddings
                logger.warning("Legacy cache does not match current documents.")
                return None

            # Structured metadata validation
            metadata: Dict[str, Any] = raw_metadata
            if metadata.get("num_documents") != len(documents):
                logger.warning(
                    f"Cache invalid: document count mismatch "
                    f"({metadata.get('num_documents')} cached vs {len(documents)} actual)."
                )
                return None

            if metadata.get("embedding_dim") != expected_dim:
                logger.warning(
                    f"Cache invalid: embedding dimension mismatch "
                    f"({metadata.get('embedding_dim')} cached vs {expected_dim} expected)."
                )
                return None

            if metadata.get("model_name") != expected_model_name:
                logger.warning(
                    f"Cache invalid: model name mismatch "
                    f"('{metadata.get('model_name')}' cached vs '{expected_model_name}' requested)."
                )
                return None

            # Verify corpus fingerprint or document IDs
            cached_fingerprint = metadata.get("corpus_fingerprint")
            if cached_fingerprint and cached_fingerprint != corpus_fingerprint:
                logger.warning("Cache invalid: corpus fingerprint changed.")
                return None

            cached_doc_ids = metadata.get("doc_ids", [])
            actual_doc_ids = [doc["id"] for doc in documents]
            if cached_doc_ids and cached_doc_ids != actual_doc_ids:
                logger.warning("Cache invalid: document IDs mismatch or order changed.")
                return None

            # Verify numpy array shape and type
            if embeddings.ndim != 2 or embeddings.shape != (len(documents), expected_dim):
                logger.warning(
                    f"Cache invalid: numpy array shape mismatch {embeddings.shape} vs ({len(documents)}, {expected_dim})."
                )
                return None

            logger.info("Successfully loaded valid document embedding cache.")
            return embeddings

        except Exception as e:
            logger.warning(f"Error loading embedding cache ({str(e)}). Rebuilding cache.")
            return None

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        documents: List[Dict[str, str]],
        model_name: str,
        embedding_dim: int,
        corpus_fingerprint: str
    ) -> None:
        """Atomically write embeddings `.npy` and `metadata.json`."""
        self.embeddings_path.parent.mkdir(parents=True, exist_ok=True)

        doc_ids = [doc["id"] for doc in documents]
        metadata = {
            "version": CACHE_VERSION,
            "model_name": model_name,
            "embedding_dim": embedding_dim,
            "num_documents": len(documents),
            "corpus_fingerprint": corpus_fingerprint,
            "doc_ids": doc_ids,
        }

        tmp_emb_path = self.embeddings_path.with_name(self.embeddings_path.stem + "_tmp.npy")
        tmp_meta_path = self.metadata_path.with_name(self.metadata_path.stem + "_tmp.json")

        try:
            np.save(tmp_emb_path, embeddings)
            with open(tmp_meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            tmp_emb_path.replace(self.embeddings_path)
            tmp_meta_path.replace(self.metadata_path)

            logger.info(f"Persisted embedding cache to {self.embeddings_path}")
        except Exception as e:
            if tmp_emb_path.exists():
                tmp_emb_path.unlink()
            if tmp_meta_path.exists():
                tmp_meta_path.unlink()
            raise CacheError(f"Failed to save embedding cache: {str(e)}") from e
