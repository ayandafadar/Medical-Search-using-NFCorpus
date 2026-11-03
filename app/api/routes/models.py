from fastapi import APIRouter
from app.schemas.models import ModelInfo, ModelsResponse
from app.core.config import settings

router = APIRouter()


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List available retrieval models",
    description="Returns metadata and descriptions for all supported retrieval engines."
)
def list_models() -> ModelsResponse:
    models = [
        ModelInfo(
            id="rrf",
            name="Reciprocal Rank Fusion (Hybrid)",
            description="Fuses TF-IDF, BM25, and Semantic rankings using 1-based RRF positional scoring.",
            type="hybrid"
        ),
        ModelInfo(
            id="semantic",
            name=f"Semantic Search ({settings.MODEL_NAME})",
            description="Dense retrieval using pre-normalized sentence transformer embeddings and cosine similarity.",
            type="neural"
        ),
        ModelInfo(
            id="bm25",
            name="BM25 Okapi",
            description="Probabilistic lexical search using spaCy lemmatization and medical negation preservation.",
            type="lexical"
        ),
        ModelInfo(
            id="tfidf",
            name="TF-IDF",
            description="Classic vector space model using term frequency-inverse document frequency and unigram/bigram n-grams.",
            type="lexical"
        ),
    ]
    return ModelsResponse(models=models)
