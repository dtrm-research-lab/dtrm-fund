"""Sample weighting utilities for legacy DTRM training."""

from collections import Counter
from collections.abc import Hashable, Sequence

import numpy as np # type: ignore


def legacy_news_weights(
    news_ids: Sequence[Hashable],
) -> np.ndarray:
    """
    Assign each row weight = 1 / number of rows sharing its news_id.

    This reproduces the legacy notebook behavior so that every
    news item contributes total weight 1 regardless of how many
    ticker-pair rows it generates.
    """

    counts = Counter(news_ids)

    return np.asarray(
        [
            1.0 / float(counts[news_id])
            for news_id in news_ids
        ],
        dtype=np.float32,
    )