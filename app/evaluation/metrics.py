import math
from typing import Any, Dict, List, Set, Tuple


def calculate_precision_at_k(retrieved_ids: List[str], relevant_dict: Dict[str, int], k: int = 10) -> float:
    """
    Calculate Precision@k for a query.
    Binary relevance: score >= 1 is considered relevant.
    """
    if k <= 0:
        return 0.0
    top_k_ids = retrieved_ids[:k]
    if not top_k_ids:
        return 0.0

    relevant_count = sum(1 for doc_id in top_k_ids if relevant_dict.get(doc_id, 0) >= 1)
    return float(relevant_count) / float(k)


def calculate_recall_at_k(retrieved_ids: List[str], relevant_dict: Dict[str, int], k: int = 10) -> float:
    """
    Calculate Recall@k for a query.
    Binary relevance: score >= 1 is considered relevant.
    """
    total_relevant = sum(1 for score in relevant_dict.values() if score >= 1)
    if total_relevant == 0:
        return 0.0

    top_k_ids = retrieved_ids[:k]
    retrieved_relevant = sum(1 for doc_id in top_k_ids if relevant_dict.get(doc_id, 0) >= 1)
    return float(retrieved_relevant) / float(total_relevant)


def calculate_average_precision(retrieved_ids: List[str], relevant_dict: Dict[str, int]) -> float:
    """
    Calculate Average Precision (AP) for a query over the full retrieved list.
    Binary relevance: score >= 1 is considered relevant.
    """
    total_relevant = sum(1 for score in relevant_dict.values() if score >= 1)
    if total_relevant == 0:
        return 0.0

    hits = 0
    sum_precisions = 0.0

    for i, doc_id in enumerate(retrieved_ids, start=1):
        if relevant_dict.get(doc_id, 0) >= 1:
            hits += 1
            precision_at_i = float(hits) / float(i)
            sum_precisions += precision_at_i

    return sum_precisions / float(total_relevant)


def calculate_ndcg_at_k(retrieved_ids: List[str], relevant_dict: Dict[str, int], k: int = 10) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at k (nDCG@k) using graded relevance.
    Formula: DCG@k = sum_{i=1}^k (2^{rel_i} - 1) / log2(i + 1)
    """
    if k <= 0:
        return 0.0

    top_k_ids = retrieved_ids[:k]
    
    # Calculate DCG@k
    dcg = 0.0
    for i, doc_id in enumerate(top_k_ids, start=1):
        rel = relevant_dict.get(doc_id, 0)
        if rel > 0:
            dcg += (math.pow(2, rel) - 1.0) / math.log2(i + 1)

    # Calculate Ideal DCG@k (IDCG@k) by sorting all ground-truth relevant scores descending
    all_rel_scores = sorted(list(relevant_dict.values()), reverse=True)
    idcg = 0.0
    for i, rel in enumerate(all_rel_scores[:k], start=1):
        if rel > 0:
            idcg += (math.pow(2, rel) - 1.0) / math.log2(i + 1)

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def calculate_precision_recall_curve(
    retrieved_dict: Dict[str, List[str]],
    qrels: Dict[str, Dict[str, int]],
    cutoffs: List[int] = None
) -> List[Dict[str, Any]]:
    """
    Calculate average Precision and Recall across various rank cutoffs to form a Precision-Recall curve.
    """
    if cutoffs is None:
        cutoffs = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100]

    valid_query_ids = [
        qid for qid, rel_map in qrels.items()
        if sum(1 for s in rel_map.values() if s >= 1) > 0
    ]

    if not valid_query_ids:
        return []

    curve_points = []
    for k in cutoffs:
        precisions = [
            calculate_precision_at_k(retrieved_dict.get(qid, []), qrels[qid], k=k)
            for qid in valid_query_ids
        ]
        recalls = [
            calculate_recall_at_k(retrieved_dict.get(qid, []), qrels[qid], k=k)
            for qid in valid_query_ids
        ]

        avg_p = sum(precisions) / len(valid_query_ids)
        avg_r = sum(recalls) / len(valid_query_ids)

        curve_points.append({
            "k": k,
            "precision": round(avg_p, 4),
            "recall": round(avg_r, 4)
        })

    return curve_points


def evaluate_retrieval_run(
    retrieved_dict: Dict[str, List[str]],
    qrels: Dict[str, Dict[str, int]],
    k: int = 10
) -> Dict[str, float]:
    """
    Evaluate a full retrieval run across all query IDs.
    """
    precisions = []
    recalls = []
    aps = []
    ndcgs = []

    evaluated_queries = 0

    for query_id, relevant_docs in qrels.items():
        total_rel = sum(1 for score in relevant_docs.values() if score >= 1)
        if total_rel == 0:
            continue

        retrieved_ids = retrieved_dict.get(query_id, [])

        p_k = calculate_precision_at_k(retrieved_ids, relevant_docs, k=k)
        r_k = calculate_recall_at_k(retrieved_ids, relevant_docs, k=k)
        ap = calculate_average_precision(retrieved_ids, relevant_docs)
        ndcg_k = calculate_ndcg_at_k(retrieved_ids, relevant_docs, k=k)

        precisions.append(p_k)
        recalls.append(r_k)
        aps.append(ap)
        ndcgs.append(ndcg_k)
        evaluated_queries += 1

    if evaluated_queries == 0:
        return {
            f"Precision@{k}": 0.0,
            f"Recall@{k}": 0.0,
            "MAP": 0.0,
            f"nDCG@{k}": 0.0,
            "evaluated_queries": 0
        }

    return {
        f"Precision@{k}": sum(precisions) / evaluated_queries,
        f"Recall@{k}": sum(recalls) / evaluated_queries,
        "MAP": sum(aps) / evaluated_queries,
        f"nDCG@{k}": sum(ndcgs) / evaluated_queries,
        "evaluated_queries": evaluated_queries
    }
