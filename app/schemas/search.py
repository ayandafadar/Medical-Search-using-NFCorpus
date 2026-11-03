from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="The medical search query text.",
        json_schema_extra={"example": "What are the health benefits of omega-3?"}
    )
    model: str = Field(
        default="rrf",
        description="The retrieval engine to use: 'tfidf', 'bm25', 'semantic', or 'rrf'.",
        json_schema_extra={"example": "rrf"}
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of ranked document results to return.",
        json_schema_extra={"example": 10}
    )
    enable_expansion: Optional[bool] = Field(
        default=None,
        description="Override default medical term expansion behavior."
    )

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Query string cannot be empty or whitespace-only.")
        return stripped

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        valid_models = {"tfidf", "bm25", "semantic", "rrf"}
        lower_v = v.lower().strip()
        if lower_v not in valid_models:
            raise ValueError(f"Invalid model '{v}'. Supported models: {sorted(list(valid_models))}")
        return lower_v


class SearchResult(BaseModel):
    id: str = Field(..., description="Unique document ID (e.g. MED-10).")
    title: str = Field(..., description="Document title.")
    text: str = Field(..., description="Full document text.")
    score: float = Field(..., description="Retrieval score or RRF fusion score.")
    retriever: str = Field(..., description="The retriever that generated this result.")
    matched_terms: Optional[List[str]] = Field(
        default=None,
        description="Document-specific matched terms/lemmas for keyword models."
    )
    component_ranks: Optional[Dict[str, int]] = Field(
        default=None,
        description="Per-retriever 1-based ranks for hybrid RRF."
    )
    component_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="Per-retriever raw scores for hybrid RRF."
    )


class SearchResponse(BaseModel):
    query: str = Field(..., description="The original search query.")
    expanded_query: Optional[str] = Field(
        default=None,
        description="The expanded query text if medical expansion was applied."
    )
    model: str = Field(..., description="Selected retrieval model.")
    count: int = Field(..., description="Total number of returned results.")
    results: List[SearchResult] = Field(..., description="Ranked list of search results.")
