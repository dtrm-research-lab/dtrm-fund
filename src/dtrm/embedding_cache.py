"""Legacy embedding cache loading."""

from pathlib import Path
import pickle

import numpy as np


def load_legacy_embedding_cache(
    dat_path: str | Path,
    shape_path: str | Path,
    index_path: str | Path,
) -> tuple[np.memmap, dict]:
    """Load a trusted legacy SBERT embedding memmap and its news index."""

    dat_path = Path(dat_path)
    shape_path = Path(shape_path)
    index_path = Path(index_path)

    with shape_path.open("rb") as f:
        shape = pickle.load(f)

    with index_path.open("rb") as f:
        news_index = pickle.load(f)

    if tuple(shape)[1:] != (384,):
        raise ValueError("legacy embeddings must have 384 dimensions.")

    if len(news_index) != shape[0]:
        raise ValueError("embedding index size does not match embedding rows.")

    embeddings = np.memmap(
        dat_path,
        dtype=np.float32,
        mode="r",
        shape=tuple(shape),
    )

    return embeddings, news_index

def embeddings_for_news_ids(
    embeddings: np.ndarray,
    news_index: dict,
    news_ids,
) -> np.ndarray:
    """Return legacy embeddings in exactly the requested news_id order."""

    news_ids = list(news_ids)

    idx = np.fromiter(
        (news_index[nid] for nid in news_ids),
        dtype=np.int32,
        count=len(news_ids),
    )

    return np.asarray(
        embeddings[idx],
        dtype=np.float32,
    )