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