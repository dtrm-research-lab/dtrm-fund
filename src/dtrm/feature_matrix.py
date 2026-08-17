"""Legacy model feature assembly."""

import numpy as np


def assemble_legacy_features(
    embedding: np.ndarray,
    text_features: np.ndarray,
    beta_pre: float,
    ret_spy_evt: float,
) -> np.ndarray:
    """
    Assemble one legacy DTRM feature row.

    Layout:
        384 embedding
        5 text features
        1 beta_pre
        1 ret_spy_evt

    Total: 391 float32 features.
    """

    embedding = np.asarray(embedding, dtype=np.float32)
    text_features = np.asarray(text_features, dtype=np.float32)

    if embedding.shape != (384,):
        raise ValueError("embedding must contain exactly 384 values.")

    if text_features.shape != (5,):
        raise ValueError("text_features must contain exactly 5 values.")

    row = np.concatenate(
        [
            embedding,
            text_features,
            np.asarray(
                [beta_pre, ret_spy_evt],
                dtype=np.float32,
            ),
        ]
    )

    return np.ascontiguousarray(row, dtype=np.float32)

def assemble_legacy_feature_matrix(
    embeddings: np.ndarray,
    text_features: np.ndarray,
    beta_pre: np.ndarray,
    ret_spy_evt: np.ndarray,
) -> np.ndarray:
    """Assemble the legacy DTRM model matrix: 384 + 5 + 1 + 1 = 391."""

    embeddings = np.asarray(embeddings, dtype=np.float32)
    text_features = np.asarray(text_features, dtype=np.float32)
    beta_pre = np.asarray(beta_pre, dtype=np.float32).reshape(-1, 1)
    ret_spy_evt = np.asarray(ret_spy_evt, dtype=np.float32).reshape(-1, 1)

    if embeddings.ndim != 2 or embeddings.shape[1] != 384:
        raise ValueError("embeddings must have shape (n, 384).")

    if text_features.ndim != 2 or text_features.shape[1] != 5:
        raise ValueError("text_features must have shape (n, 5).")

    n = embeddings.shape[0]

    if (
        text_features.shape[0] != n
        or beta_pre.shape[0] != n
        or ret_spy_evt.shape[0] != n
    ):
        raise ValueError("all feature blocks must contain the same number of rows.")

    X = np.concatenate(
        [
            embeddings,
            text_features,
            beta_pre,
            ret_spy_evt,
        ],
        axis=1,
    )

    return np.ascontiguousarray(X, dtype=np.float32)

def assemble_exante_feature_matrix(
    embeddings: np.ndarray,
    text_features: np.ndarray,
    beta_pre: np.ndarray,
) -> np.ndarray:
    """
    Assemble the ex-ante DTRM model matrix.

    Layout:
        384 embedding
        5 text features
        1 beta_pre

    Total: 390 float32 features.

    Future-inclusive ret_spy_evt is intentionally excluded.
    """

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    text_features = np.asarray(
        text_features,
        dtype=np.float32,
    )

    beta_pre = np.asarray(
        beta_pre,
        dtype=np.float32,
    ).reshape(-1, 1)

    if (
        embeddings.ndim != 2
        or embeddings.shape[1] != 384
    ):
        raise ValueError(
            "embeddings must have shape (n, 384)."
        )

    if (
        text_features.ndim != 2
        or text_features.shape[1] != 5
    ):
        raise ValueError(
            "text_features must have shape (n, 5)."
        )

    n = embeddings.shape[0]

    if (
        text_features.shape[0] != n
        or beta_pre.shape[0] != n
    ):
        raise ValueError(
            "all feature blocks must contain the same number of rows."
        )

    X = np.concatenate(
        [
            embeddings,
            text_features,
            beta_pre,
        ],
        axis=1,
    )

    return np.ascontiguousarray(
        X,
        dtype=np.float32,
    )