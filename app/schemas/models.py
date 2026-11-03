from typing import List
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "rrf"})
    name: str = Field(..., json_schema_extra={"example": "Reciprocal Rank Fusion (Hybrid)"})
    description: str = Field(..., json_schema_extra={"example": "Combines TF-IDF, BM25, and Semantic rankings."})
    type: str = Field(..., json_schema_extra={"example": "hybrid"})


class ModelsResponse(BaseModel):
    models: List[ModelInfo] = Field(...)
