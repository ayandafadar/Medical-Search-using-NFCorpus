from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import models, search
from app.core.config import settings


def create_test_app(retrieval_service):
    app = FastAPI()
    app.state.retrieval_service = retrieval_service
    app.include_router(search.router, prefix=settings.API_V1_STR)
    app.include_router(models.router, prefix=settings.API_V1_STR)
    return app


def test_search_endpoint_all_models(initialized_retrieval_service):
    app = create_test_app(initialized_retrieval_service)
    client = TestClient(app)

    for model_name in ["tfidf", "bm25", "semantic", "rrf"]:
        payload = {
            "query": "high blood pressure hypertension",
            "model": model_name,
            "top_k": 2
        }
        response = client.post(f"{settings.API_V1_STR}/search", json=payload)
        assert response.status_code == 200, f"Failed for model {model_name}"
        data = response.json()

        assert data["query"] == payload["query"]
        assert data["model"] == model_name
        assert data["count"] <= 2
        assert len(data["results"]) <= 2

        if data["results"]:
            first = data["results"][0]
            assert "id" in first
            assert "title" in first
            assert "text" in first
            assert "score" in first
            assert "retriever" in first


def test_search_endpoint_invalid_model(initialized_retrieval_service):
    app = create_test_app(initialized_retrieval_service)
    client = TestClient(app)

    payload = {
        "query": "diabetes",
        "model": "invalid_model_name",
        "top_k": 5
    }
    response = client.post(f"{settings.API_V1_STR}/search", json=payload)
    assert response.status_code == 422  # Pydantic validation error for invalid enum/model


def test_search_endpoint_empty_query(initialized_retrieval_service):
    app = create_test_app(initialized_retrieval_service)
    client = TestClient(app)

    payload = {
        "query": "   ",
        "model": "rrf",
        "top_k": 5
    }
    response = client.post(f"{settings.API_V1_STR}/search", json=payload)
    assert response.status_code == 422  # Pydantic query min_length validation error


def test_models_endpoint():
    app = FastAPI()
    app.include_router(models.router, prefix=settings.API_V1_STR)
    client = TestClient(app)

    response = client.get(f"{settings.API_V1_STR}/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    model_ids = [m["id"] for m in data["models"]]
    assert "tfidf" in model_ids
    assert "bm25" in model_ids
    assert "semantic" in model_ids
    assert "rrf" in model_ids
