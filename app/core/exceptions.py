class MedicalSearchError(Exception):
    """Base exception class for Medical Search application."""
    pass


class CorpusLoadError(MedicalSearchError):
    """Raised when loading or validating the corpus fails."""
    pass


class CacheError(MedicalSearchError):
    """Raised when reading or writing embedding cache fails."""
    pass


class RetrievalInitializationError(MedicalSearchError):
    """Raised when a retrieval model or index fails to initialize."""
    pass


class InvalidQueryError(MedicalSearchError):
    """Raised when an invalid query is passed to retrieval engines."""
    pass


class ServiceNotReadyError(MedicalSearchError):
    """Raised when API requests are received before initialization completes."""
    pass
