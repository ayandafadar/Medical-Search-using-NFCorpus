import math
from app.evaluation.metrics import (
    calculate_average_precision,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
    evaluate_retrieval_run,
)


def test_precision_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    qrels = {"doc1": 1, "doc3": 2, "doc6": 1}

    p3 = calculate_precision_at_k(retrieved, qrels, k=3)
    # Among doc1, doc2, doc3 -> doc1(1) and doc3(2) are relevant => 2/3
    assert abs(p3 - (2.0 / 3.0)) < 1e-5


def test_recall_at_k():
    retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    qrels = {"doc1": 1, "doc3": 2, "doc6": 1}

    r3 = calculate_recall_at_k(retrieved, qrels, k=3)
    # Total relevant docs in qrels = 3 (doc1, doc3, doc6).
    # Retrieved in top 3: doc1, doc3 => 2/3
    assert abs(r3 - (2.0 / 3.0)) < 1e-5


def test_average_precision():
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    qrels = {"doc1": 1, "doc3": 1}

    # At rank 1: doc1 hit => P@1 = 1/1 = 1.0
    # At rank 2: doc2 miss
    # At rank 3: doc3 hit => P@3 = 2/3
    # AP = (1.0 + 2/3) / 2 = (5/3) / 2 = 5/6 = 0.83333...
    ap = calculate_average_precision(retrieved, qrels)
    assert abs(ap - (5.0 / 6.0)) < 1e-5


def test_ndcg_at_k():
    retrieved = ["doc1", "doc2", "doc3"]
    qrels = {"doc1": 2, "doc2": 0, "doc3": 1}

    # DCG@3 = (2^2 - 1)/log2(2) + (2^0 - 1)/log2(3) + (2^1 - 1)/log2(4)
    #       = 3 / 1.0 + 0 + 1 / 2.0 = 3.5
    # Ideal ranking scores: doc1(2), doc3(1)
    # IDCG@3 = (2^2 - 1)/log2(2) + (2^1 - 1)/log2(3) = 3 + 1/log2(3) = 3 + 0.63092975 = 3.63092975
    # nDCG@3 = 3.5 / 3.63092975
    ndcg = calculate_ndcg_at_k(retrieved, qrels, k=3)

    dcg_expected = 3.0 + 0.0 + 0.5
    idcg_expected = 3.0 + 1.0 / math.log2(3)
    expected_ndcg = dcg_expected / idcg_expected

    assert abs(ndcg - expected_ndcg) < 1e-5


def test_evaluate_retrieval_run():
    retrieved_dict = {
        "q1": ["doc1", "doc2", "doc3"],
        "q2": ["doc10", "doc11"]
    }
    qrels = {
        "q1": {"doc1": 1, "doc3": 2},
        "q2": {"doc10": 2}
    }

    report = evaluate_retrieval_run(retrieved_dict, qrels, k=3)
    assert "Precision@3" in report
    assert "Recall@3" in report
    assert "MAP" in report
    assert "nDCG@3" in report
    assert report["evaluated_queries"] == 2
