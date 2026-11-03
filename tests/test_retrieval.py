from app.retrieval.bm25 import BM25Retriever
from app.retrieval.rrf import HybridRRFRetriever
from app.retrieval.semantic import SemanticRetriever
from app.retrieval.tfidf import TFIDFRetriever


def test_tfidf_retriever(sample_documents):
    retriever = TFIDFRetriever(sample_documents)
    results = retriever.search("blood pressure salt", top_k=2)
    assert len(results) > 0
    assert results[0]["id"] == "DOC-1"
    assert results[0]["retriever"] == "tfidf"


def test_bm25_retriever_and_negation_preservation(sample_documents):
    retriever = BM25Retriever(sample_documents, spacy_model="en_core_web_sm")

    # Test query containing negation terms 'no' and 'without'
    query_tokens = retriever.preprocess_query("statin therapy without side effects no risk")
    assert "without" in query_tokens
    assert "no" in query_tokens

    results = retriever.search("statin therapy without side effects no risk", top_k=2)
    assert len(results) > 0
    assert results[0]["id"] == "DOC-4"
    assert "matched_terms" in results[0]
    assert "without" in results[0]["matched_terms"] or "no" in results[0]["matched_terms"]


def test_semantic_retriever(sample_documents, mock_sentence_transformer):
    embeddings = mock_sentence_transformer.encode([d["content"] for d in sample_documents])
    retriever = SemanticRetriever(sample_documents, mock_sentence_transformer, embeddings)

    results = retriever.search("insulin diabetes mellitus", top_k=2)
    assert len(results) == 2
    assert results[0]["retriever"] == "semantic"


def test_rrf_retriever_scoring_and_tie_breaking(sample_documents, mock_sentence_transformer):
    tfidf_engine = TFIDFRetriever(sample_documents)
    bm25_engine = BM25Retriever(sample_documents, spacy_model="en_core_web_sm")
    embeddings = mock_sentence_transformer.encode([d["content"] for d in sample_documents])
    semantic_engine = SemanticRetriever(sample_documents, mock_sentence_transformer, embeddings)

    rrf_engine = HybridRRFRetriever(
        documents=sample_documents,
        tfidf_retriever=tfidf_engine,
        bm25_retriever=bm25_engine,
        semantic_retriever=semantic_engine,
        rrf_k=60,
        candidate_k=10
    )

    results = rrf_engine.search("myocardial infarction heart attack", top_k=2)
    assert len(results) > 0
    first = results[0]
    assert first["id"] == "DOC-3"
    assert "component_ranks" in first
    assert "component_scores" in first
    assert "tfidf" in first["component_ranks"]
    assert "bm25" in first["component_ranks"]
    assert "semantic" in first["component_ranks"]
