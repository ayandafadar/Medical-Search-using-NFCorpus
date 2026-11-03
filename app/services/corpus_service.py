import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from app.core.exceptions import CorpusLoadError
from app.core.logging import logger


class CorpusService:
    """Service responsible for loading, indexing, and fingerprinting the medical corpus."""

    def __init__(self, corpus_path: Path):
        self.corpus_path = corpus_path
        self.documents: List[Dict[str, str]] = []
        self.doc_map: Dict[str, Dict[str, str]] = {}
        self.fingerprint: str = ""

    def load(self) -> List[Dict[str, str]]:
        """Load documents from JSONL file and compute corpus fingerprint."""
        if not self.corpus_path.exists():
            raise CorpusLoadError(f"Corpus file not found at: {self.corpus_path}")

        documents = []
        doc_map = {}
        hasher = hashlib.sha256()

        try:
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    item = json.loads(stripped)
                    doc_id = item.get("_id")
                    if not doc_id:
                        continue

                    title = item.get("title", "")
                    text = item.get("text", "")
                    content = f"{title} {text}".strip()

                    doc = {
                        "id": doc_id,
                        "title": title,
                        "text": text,
                        "content": content,
                    }
                    documents.append(doc)
                    doc_map[doc_id] = doc

                    # Hash doc_id and content for fingerprinting
                    hasher.update(doc_id.encode("utf-8"))
                    hasher.update(content.encode("utf-8"))

        except Exception as e:
            raise CorpusLoadError(f"Failed to read corpus file: {str(e)}") from e

        if not documents:
            raise CorpusLoadError(f"Corpus file at {self.corpus_path} is empty.")

        self.documents = documents
        self.doc_map = doc_map
        self.fingerprint = hasher.hexdigest()

        logger.info(
            f"Successfully loaded {len(self.documents)} documents from {self.corpus_path.name} "
            f"(Fingerprint: {self.fingerprint[:12]}...)"
        )
        return self.documents

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, str]]:
        """Retrieve document metadata by document ID."""
        return self.doc_map.get(doc_id)

    @property
    def document_count(self) -> int:
        return len(self.documents)
