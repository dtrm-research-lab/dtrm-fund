import numpy as np

from dtrm.text_features import legacy_text_features
from dtrm.text_features import legacy_truncate_text
from dtrm.text_features import legacy_text_feature_matrix


def test_legacy_text_features():
    result = legacy_text_features("  HELLO world!?  ")

    expected = np.asarray(
        [
            np.log1p(13),  # len("HELLO world!?")
            np.log1p(2),
            np.log1p(1),
            np.log1p(1),
            5 / (13 + 1e-9),
        ],
        dtype=np.float32,
    )

    np.testing.assert_allclose(result, expected)
    assert result.dtype == np.float32
    assert result.shape == (5,)

def test_legacy_truncate_text():
    text = "ABC\nDEF\r" + ("x" * 2000)

    result = legacy_truncate_text(text)

    assert "\n" not in result
    assert "\r" not in result
    assert result.startswith("ABC DEF ")
    assert len(result) == 1600

def test_legacy_text_feature_matrix_preserves_order():
    texts = [
        "HELLO world!",
        "Second text?",
    ]

    X = legacy_text_feature_matrix(texts)

    assert X.shape == (2, 5)
    assert X.dtype == np.float32
    assert X.flags["C_CONTIGUOUS"]

    np.testing.assert_array_equal(
        X[0],
        legacy_text_features(texts[0]),
    )
    np.testing.assert_array_equal(
        X[1],
        legacy_text_features(texts[1]),
    )