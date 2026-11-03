from fastapi import HTTPException, Request, status
from app.services.retrieval_service import RetrievalService


def get_retrieval_service(request: Request) -> RetrievalService:
    """FastAPI dependency to retrieve the shared RetrievalService instance from app state."""
    service: RetrievalService = getattr(request.app.state, "retrieval_service", None)
    if service is None or not service.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Retrieval service is initializing or unavailable."
        )
    return service
