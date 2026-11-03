import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, status
from app.core.config import settings

router = APIRouter()


@router.get(
    "/evaluation/results",
    summary="Get precomputed evaluation benchmark metrics and precision-recall curves",
    description="Returns precomputed evaluation metrics (P@10, Recall@10, MAP, nDCG@10) and precision-recall curves for test or dev splits."
)
def get_evaluation_results(split: str = Query(default="test", regex="^(test|dev|train)$")):
    results_dir = settings.abs_results_dir
    report_path = results_dir / f"evaluation_{split}.json"

    if not report_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation results for split '{split}' not found. Please run the evaluation benchmark script first."
        )

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load evaluation results: {str(e)}"
        )
