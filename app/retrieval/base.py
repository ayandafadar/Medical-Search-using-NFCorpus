from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseRetriever(ABC):
    """Abstract base class for all retrieval engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name/identifier of the retriever."""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Execute search query and return ranked document dicts.

        Each dictionary must contain:
          - id: str
          - title: str
          - text: str
          - score: float
          - retriever: str
        """
        pass
