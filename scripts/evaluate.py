import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.services.retrieval_service import RetrievalService
from app.services.evaluation_service import EvaluationService


def main():
    parser = argparse.ArgumentParser(description="Run NFCorpus Offline Retrieval Evaluation")
    parser.add_argument("--split", type=str, default="test", choices=["dev", "test", "train"], help="Qrels split to evaluate (default: test)")
    parser.add_argument("--top-k", type=int, default=100, help="Candidate rank depth to evaluate (default: 100)")
    parser.add_argument("--metric-k", type=int, default=10, help="Cutoff rank k for metrics like P@k, R@k, nDCG@k (default: 10)")
    parser.add_argument("--expansion", action="store_true", help="Enable medical term expansion during evaluation")
    args = parser.parse_args()

    setup_logging()
    logger.info("Initializing RetrievalService for offline evaluation...")

    retrieval_service = RetrievalService(settings)
    retrieval_service.initialize()

    eval_service = EvaluationService(settings, retrieval_service)
    results = eval_service.run_benchmark(
        split=args.split,
        top_k_evaluation=args.top_k,
        metric_k=args.metric_k,
        enable_expansion=args.expansion
    )

    print("\n" + "=" * 80)
    print(f"OFFLINE RETRIEVAL EVALUATION REPORT (Split: {args.split.upper()}, Expansion: {args.expansion})")
    print("=" * 80)
    print(f"{'Model':<15} | {'P@' + str(args.metric_k):<10} | {'Recall@' + str(args.metric_k):<12} | {'MAP':<10} | {'nDCG@' + str(args.metric_k):<10}")
    print("-" * 80)

    for model_name, metrics in results.items():
        p_val = metrics.get(f"Precision@{args.metric_k}", 0.0)
        r_val = metrics.get(f"Recall@{args.metric_k}", 0.0)
        map_val = metrics.get("MAP", 0.0)
        ndcg_val = metrics.get(f"nDCG@{args.metric_k}", 0.0)

        print(f"{model_name.upper():<15} | {p_val:<10.4f} | {r_val:<12.4f} | {map_val:<10.4f} | {ndcg_val:<10.4f}")

    print("=" * 80)
    print(f"Detailed results saved to: {settings.abs_results_dir / f'evaluation_{args.split}.json'}\n")


if __name__ == "__main__":
    main()
