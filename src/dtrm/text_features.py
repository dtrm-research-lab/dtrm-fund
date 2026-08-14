"""Legacy text feature construction."""

import numpy as np


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

    if not isinstance(text, str):
        text = "" if text is None else str(text)

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