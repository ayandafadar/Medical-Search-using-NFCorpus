from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.schemas.health import HealthResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service health and readiness",
    description="Returns service readiness, active retrievers status, document count, and embedding cache status."
)
def get_health(request: Request) -> HealthResponse:
    service: RetrievalService = getattr(request.app.state, "retrieval_service", None)
    if service is None or not service.ready:
        health_data = (
            service.get_health_status()
            if service is not None
            else {
                "status": "unhealthy",
                "initialized": False,
                "retrievers": {},
                "cache_status": "uninitialized",
                "document_count": 0,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )

    return HealthResponse(**service.get_health_status())
