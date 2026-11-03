from typing import Dict, List
from unittest.mock import MagicMock
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.rrf import HybridRRFRetriever
from app.retrieval.semantic import SemanticRetriever
from app.retrieval.tfidf import TFIDFRetriever
from app.services.expansion_service import MedicalExpansionService
from app.services.retrieval_service import RetrievalService


@pytest.fixture
def sample_documents() -> List[Dict[str, str]]:
    return [
        {
            "id": "DOC-1",
            "title": "Hypertension Treatment Guidelines",
            "text": "High blood pressure can be managed with anti-hypertensive drugs and lifestyle modifications. Patients should avoid excess salt.",
            "content": "Hypertension Treatment Guidelines High blood pressure can be managed with anti-hypertensive drugs and lifestyle modifications. Patients should avoid excess salt."
        },
        {
            "id": "DOC-2",
            "title": "Diabetes Mellitus Management",
            "text": "Insulin therapy and metformin are standard treatments for type 2 diabetes mellitus to regulate high blood sugar levels.",
            "content": "Diabetes Mellitus Management Insulin therapy and metformin are standard treatments for type 2 diabetes mellitus to regulate high blood sugar levels."
        },
        {
            "id": "DOC-3",
            "title": "Heart Attack and Myocardial Infarction",
            "text": "Myocardial infarction symptoms include chest pain and shortness of breath. Immediate medical attention is required.",
            "content": "Heart Attack and Myocardial Infarction Myocardial infarction symptoms include chest pain and shortness of breath. Immediate medical attention is required."
        },
        {
            "id": "DOC-4",
            "title": "Statin Therapy without Complications",
            "text": "Statin drugs show no adverse side effects in most cohort studies. There is no evidence of increased risk.",
            "content": "Statin Therapy without Complications Statin drugs show no adverse side effects in most cohort studies. There is no evidence of increased risk."
        }
    ]


@pytest.fixture
def mock_sentence_transformer():
    mock_model = MagicMock()
    mock_model.get_sentence_embedding_dimension.return_value = 384
    mock_model.get_embedding_dimension.return_value = 384
    # Mock encode to return deterministic normalized 384-d vectors
    def mock_encode(texts, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
        arr = np.zeros((len(texts), 384), dtype=np.float32)
        for i, text in enumerate(texts):
            # Fill with pseudo deterministic values based on text length
            arr[i, :10] = len(text) % 10 + 1.0
        # Normalize
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms if kwargs.get("convert_to_numpy", True) else arr

    mock_model.encode.side_effect = mock_encode
    return mock_model


@pytest.fixture
def mock_settings(tmp_path) -> Settings:
    data_dir = tmp_path / "data"
    embeddings_dir = tmp_path / "embeddings"
    results_dir = tmp_path / "results"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        PROJECT_NAME="Test Medical Search API",
        DATA_DIR=data_dir,
        EMBEDDINGS_DIR=embeddings_dir,
        RESULTS_DIR=results_dir,
        SPACY_MODEL="en_core_web_sm",
        MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2",
        RRF_K=60,
        RRF_CANDIDATE_K=10
    )


@pytest.fixture
def initialized_retrieval_service(sample_documents, mock_sentence_transformer, mock_settings):
    service = RetrievalService(mock_settings)
    service.corpus_service.documents = sample_documents
    service.corpus_service.doc_map = {doc["id"]: doc for doc in sample_documents}
    service.corpus_service.fingerprint = "dummy_test_fingerprint_123"

    tfidf_engine = TFIDFRetriever(sample_documents)
    bm25_engine = BM25Retriever(sample_documents, spacy_model=mock_settings.SPACY_MODEL)

    st_dim = mock_sentence_transformer.get_sentence_embedding_dimension()
    embeddings = mock_sentence_transformer.encode([doc["content"] for doc in sample_documents])

    semantic_engine = SemanticRetriever(
        documents=sample_documents,
        model=mock_sentence_transformer,
        document_embeddings=embeddings
    )

    rrf_engine = HybridRRFRetriever(
        documents=sample_documents,
        tfidf_retriever=tfidf_engine,
        bm25_retriever=bm25_engine,
        semantic_retriever=semantic_engine,
        rrf_k=60,
        candidate_k=10
    )

    service.st_model = mock_sentence_transformer
    service.document_embeddings = embeddings
    service.retrievers = {
        "tfidf": tfidf_engine,
        "bm25": bm25_engine,
        "semantic": semantic_engine,
        "rrf": rrf_engine
    }
    service.ready = True
    service.cache_status = "test_mock"
    return service
