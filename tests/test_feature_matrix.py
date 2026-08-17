import numpy as np

from dtrm.feature_matrix import assemble_legacy_features
from dtrm.feature_matrix import assemble_legacy_feature_matrix
from dtrm.feature_matrix import assemble_exante_feature_matrix


def test_assemble_legacy_features():
    embedding = np.arange(384, dtype=np.float32)
    text_features = np.asarray(
        [1, 2, 3, 4, 5],
        dtype=np.float32,
    )

    row = assemble_legacy_features(
        embedding,
        text_features,
        beta_pre=1.25,
        ret_spy_evt=-0.10,
    )

    assert row.shape == (391,)
    assert row.dtype == np.float32

    np.testing.assert_array_equal(row[:384], embedding)
    np.testing.assert_array_equal(row[384:389], text_features)

    assert row[389] == np.float32(1.25)
    assert row[390] == np.float32(-0.10)

def test_assemble_legacy_feature_matrix():
    embeddings = np.arange(2 * 384, dtype=np.float32).reshape(2, 384)

    text_features = np.asarray(
        [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
        ],
        dtype=np.float32,
    )

    beta_pre = np.asarray([1.25, 0.80], dtype=np.float32)
    ret_spy_evt = np.asarray([-0.10, 0.05], dtype=np.float32)

    X = assemble_legacy_feature_matrix(
        embeddings,
        text_features,
        beta_pre,
        ret_spy_evt,
    )

    assert X.shape == (2, 391)
    assert X.dtype == np.float32
    assert X.flags["C_CONTIGUOUS"]

    np.testing.assert_array_equal(X[:, :384], embeddings)
    np.testing.assert_array_equal(X[:, 384:389], text_features)
    np.testing.assert_array_equal(X[:, 389], beta_pre)
    np.testing.assert_array_equal(X[:, 390], ret_spy_evt)

def test_assemble_exante_feature_matrix_excludes_future_market_return():
    embeddings = np.zeros((2, 384), dtype=np.float32)
    text_features = np.zeros((2, 5), dtype=np.float32)
    beta_pre = np.asarray([1.25, 0.80], dtype=np.float32)

    X = assemble_exante_feature_matrix(
        embeddings,
        text_features,
        beta_pre,
    )

    assert X.shape == (2, 390)
    assert X.dtype == np.float32
    assert X.flags["C_CONTIGUOUS"]

    np.testing.assert_array_equal(
        X[:, 389],
        beta_pre,
    )