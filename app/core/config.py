import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Medical Search NFCorpus API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Paths (relative to project root unless absolute path provided)
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = Path("data/nfcorpus")
    EMBEDDINGS_DIR: Path = Path("embeddings")
    RESULTS_DIR: Path = Path("results")

    # Retrieval Engine Settings
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"
    RRF_K: int = 60
    RRF_CANDIDATE_K: int = 100
    MAX_TOP_K: int = 100

    # Medical Expansion
    ENABLE_MEDICAL_EXPANSION: bool = False

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:5173"]

    def get_absolute_path(self, path: Path) -> Path:
        """Resolve path relative to project root if it is not absolute."""
        if path.is_absolute():
            return path
        return (self.PROJECT_ROOT / path).resolve()

    @property
    def corpus_path(self) -> Path:
        return self.get_absolute_path(self.DATA_DIR) / "corpus.jsonl"

    @property
    def queries_path(self) -> Path:
        return self.get_absolute_path(self.DATA_DIR) / "queries.jsonl"

    @property
    def qrels_dir(self) -> Path:
        return self.get_absolute_path(self.DATA_DIR) / "qrels"

    @property
    def embeddings_path(self) -> Path:
        return self.get_absolute_path(self.EMBEDDINGS_DIR) / "document_embeddings.npy"

    @property
    def metadata_path(self) -> Path:
        return self.get_absolute_path(self.EMBEDDINGS_DIR) / "metadata.json"

    @property
    def abs_results_dir(self) -> Path:
        return self.get_absolute_path(self.RESULTS_DIR)


settings = Settings()
