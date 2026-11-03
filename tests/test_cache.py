import json
import numpy as np
from app.services.cache_service import CacheService


def test_cache_service_lifecycle(tmp_path, sample_documents):
    emb_path = tmp_path / "embeddings.npy"
    meta_path = tmp_path / "metadata.json"
    cache_service = CacheService(emb_path, meta_path)

    corpus_fingerprint = "test_fp_123"
    model_name = "test-model"
    dim = 16

    # 1. Initially cache is missing
    loaded = cache_service.load_valid_embeddings(
        sample_documents, model_name, dim, corpus_fingerprint
    )
    assert loaded is None

    # 2. Generate and save fake embeddings
    fake_embeddings = np.random.randn(len(sample_documents), dim).astype(np.float32)
    cache_service.save_embeddings(
        fake_embeddings, sample_documents, model_name, dim, corpus_fingerprint
    )

    assert emb_path.exists()
    assert meta_path.exists()

    # 3. Load valid cache
    loaded = cache_service.load_valid_embeddings(
        sample_documents, model_name, dim, corpus_fingerprint
    )
    assert loaded is not None
    assert loaded.shape == (len(sample_documents), dim)

    # 4. Invalidation on corpus fingerprint change
    loaded_stale_fp = cache_service.load_valid_embeddings(
        sample_documents, model_name, dim, "different_fingerprint"
    )
    assert loaded_stale_fp is None

    # 5. Invalidation on dimension change
    loaded_stale_dim = cache_service.load_valid_embeddings(
        sample_documents, model_name, 32, corpus_fingerprint
    )
    assert loaded_stale_dim is None

    # 6. Corrupt metadata file handling
    with open(meta_path, "w") as f:
        f.write("{invalid json...")

    loaded_corrupt = cache_service.load_valid_embeddings(
        sample_documents, model_name, dim, corpus_fingerprint
    )
    assert loaded_corrupt is None
