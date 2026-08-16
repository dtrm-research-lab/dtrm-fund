"""Legacy text feature construction."""

import numpy as np


def legacy_truncate_text(
    text: str | None,
    max_chars: int = 1600,
) -> str:
    """Reproduce legacy text normalization and truncation."""

    if not isinstance(text, str):
        text = "" if text is None else str(text)

    text = text.replace("\n", " ").replace("\r", " ")

    return text[:max_chars] if len(text) > max_chars else text


def legacy_text_features(text: str | None) -> np.ndarray:
    """
    Reproduce the 5 cheap text features from trumpDataModel_v4.

    Output order:
        n_chars_log1p
        n_words_log1p
        n_excl_log1p
        n_qm_log1p
        upper_ratio
    """

    text = legacy_truncate_text(text)
    text = text.strip()

    n_chars = len(text)
    n_words = len(text.split()) if n_chars else 0
    n_excl = text.count("!")
    n_qm = text.count("?")

    upper_ratio = (
        sum(1 for c in text if c.isupper()) / (n_chars + 1e-9)
        if n_chars
        else 0.0
    )

    values = np.asarray(
        [n_chars, n_words, n_excl, n_qm, upper_ratio],
        dtype=np.float32,
    )

    values[:4] = np.log1p(values[:4])

    return values

def legacy_text_feature_matrix(texts) -> np.ndarray:
    """Build legacy cheap text features preserving input order."""

    rows = [
        legacy_text_features(text)
        for text in texts
    ]

    if not rows:
        return np.empty((0, 5), dtype=np.float32)

    return np.ascontiguousarray(
        np.vstack(rows),
        dtype=np.float32,
    )