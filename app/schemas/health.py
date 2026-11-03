from typing import Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    initialized: bool = Field(..., json_schema_extra={"example": True})
    retrievers: Dict[str, bool] = Field(
        ...,
        json_schema_extra={"example": {"tfidf": True, "bm25": True, "semantic": True, "rrf": True}}
    )
    cache_status: str = Field(..., json_schema_extra={"example": "valid"})
    document_count: int = Field(..., json_schema_extra={"example": 3633})
