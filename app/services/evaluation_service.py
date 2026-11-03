import json
from pathlib import Path
from typing import Dict, List, Tuple
from app.core.config import Settings
from app.core.logging import logger
from app.evaluation.metrics import calculate_precision_recall_curve, evaluate_retrieval_run
from app.services.retrieval_service import RetrievalService


class EvaluationService:
    """Service for running offline IR evaluation across all models using NFCorpus qrels."""

    def __init__(self, settings: Settings, retrieval_service: RetrievalService):
        self.settings = settings
        self.retrieval_service = retrieval_service

    def load_queries(self) -> Dict[str, str]:
        """Load queries from queries.jsonl into dict {query_id: query_text}."""
        queries_path = self.settings.queries_path
        if not queries_path.exists():
            raise FileNotFoundError(f"Queries file not found at {queries_path}")

        queries = {}
        with open(queries_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                queries[item["_id"]] = item["text"]
        logger.info(f"Loaded {len(queries)} queries from {queries_path.name}")
        return queries

    def load_qrels(self, split: str = "test") -> Dict[str, Dict[str, int]]:
        """
        Load qrels TSV file.
        TSV header: query-id\tcorpus-id\tscore
        Returns {query_id: {corpus_id: score_int}}
        """
        qrels_path = self.settings.qrels_dir / f"{split}.tsv"
        if not qrels_path.exists():
            raise FileNotFoundError(f"Qrels file not found at {qrels_path}")

        qrels: Dict[str, Dict[str, int]] = {}
        with open(qrels_path, "r", encoding="utf-8") as f:
            header = f.readline()  # Skip header line
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split("\t")
                if len(parts) < 3:
                    continue
                qid, cid, score_str = parts[0], parts[1], parts[2]
                score = int(score_str)
                if qid not in qrels:
                    qrels[qid] = {}
                qrels[qid][cid] = score

        logger.info(f"Loaded qrels for {len(qrels)} queries from {qrels_path.name}")
        return qrels

    def run_benchmark(
        self,
        split: str = "test",
        top_k_evaluation: int = 100,
        metric_k: int = 10,
        enable_expansion: bool = False
    ) -> Dict[str, Dict[str, float]]:
        """
        Run comprehensive evaluation benchmark comparing TF-IDF, BM25, Semantic, and Hybrid RRF.
        """
        if not self.retrieval_service.ready:
            raise RuntimeError("RetrievalService must be initialized before running evaluation.")

        queries = self.load_queries()
        qrels = self.load_qrels(split=split)

        # Restrict queries to those present in qrels
        eval_query_ids = [qid for qid in qrels if qid in queries]
        logger.info(f"Starting evaluation benchmark on split '{split}' with {len(eval_query_ids)} queries...")

        models = ["tfidf", "bm25", "semantic", "rrf"]
        model_results: Dict[str, Dict[str, List[str]]] = {m: {} for m in models}

        for idx, qid in enumerate(eval_query_ids, start=1):
            query_text = queries[qid]
            for model_name in models:
                res = self.retrieval_service.search(
                    query=query_text,
                    model_name=model_name,
                    top_k=top_k_evaluation,
                    enable_expansion=enable_expansion
                )
                retrieved_ids = [doc["id"] for doc in res["results"]]
                model_results[model_name][qid] = retrieved_ids

            if idx % 50 == 0 or idx == len(eval_query_ids):
                logger.info(f"Evaluated {idx}/{len(eval_query_ids)} queries...")

        # Calculate metrics and precision-recall curve points for each model
        summary: Dict[str, Dict[str, float]] = {}
        pr_curves: Dict[str, List[Dict[str, Any]]] = {}

        for model_name in models:
            metrics = evaluate_retrieval_run(
                retrieved_dict=model_results[model_name],
                qrels=qrels,
                k=metric_k
            )
            summary[model_name] = metrics

            pr_points = calculate_precision_recall_curve(
                retrieved_dict=model_results[model_name],
                qrels=qrels,
                cutoffs=[1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 50, 75, 100]
            )
            pr_curves[model_name] = pr_points

        # Save results to JSON
        output_dir = self.settings.abs_results_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"evaluation_{split}.json"

        report_data = {
            "split": split,
            "metric_k": metric_k,
            "candidate_depth": top_k_evaluation,
            "enable_expansion": enable_expansion,
            "evaluated_queries": len(eval_query_ids),
            "results": summary,
            "precision_recall": pr_curves
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Saved evaluation report to {report_path}")
        return summary
