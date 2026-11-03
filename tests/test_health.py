from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import health
from app.services.retrieval_service import RetrievalService


def test_health_endpoint_not_ready():
    app = FastAPI()
    app.include_router(health.router, prefix="/api/v1")
    app.state.retrieval_service = None

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"]["status"] == "unhealthy"
    assert data["detail"]["initialized"] is False


def test_health_endpoint_ready(initialized_retrieval_service):
    app = FastAPI()
    app.include_router(health.router, prefix="/api/v1")
    app.state.retrieval_service = initialized_retrieval_service

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["initialized"] is True
    assert data["document_count"] == 4
    assert data["retrievers"]["rrf"] is True
