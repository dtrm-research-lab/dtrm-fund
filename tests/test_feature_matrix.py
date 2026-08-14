import numpy as np

from dtrm.feature_matrix import assemble_legacy_features


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