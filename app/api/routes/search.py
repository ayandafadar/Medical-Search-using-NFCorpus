from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_retrieval_service
from app.core.exceptions import InvalidQueryError
from app.schemas.search import SearchRequest, SearchResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Execute medical document search",
    description="Executes a medical search query using TF-IDF, BM25, Semantic, or RRF hybrid retrieval."
)
def search_documents(
    payload: SearchRequest,
    service: RetrievalService = Depends(get_retrieval_service)
) -> SearchResponse:
    try:
        results_data = service.search(
            query=payload.query,
            model_name=payload.model,
            top_k=payload.top_k,
            enable_expansion=payload.enable_expansion
        )
        return SearchResponse(**results_data)
    except InvalidQueryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during retrieval: {str(e)}"
        )
