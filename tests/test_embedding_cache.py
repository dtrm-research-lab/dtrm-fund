import pickle

import numpy as np

from dtrm.embedding_cache import load_legacy_embedding_cache


def test_load_legacy_embedding_cache(tmp_path):
    shape = (3, 384)
    index = {"n1": 0, "n2": 1, "n3": 2}

    data = np.arange(3 * 384, dtype=np.float32).reshape(shape)

    dat_path = tmp_path / "emb.dat"
    shape_path = tmp_path / "shape.pkl"
    index_path = tmp_path / "index.pkl"

    mem = np.memmap(
        dat_path,
        dtype=np.float32,
        mode="w+",
        shape=shape,
    )
    mem[:] = data
    mem.flush()

    with shape_path.open("wb") as f:
        pickle.dump(shape, f)

    with index_path.open("wb") as f:
        pickle.dump(index, f)

    embeddings, news_index = load_legacy_embedding_cache(
        dat_path,
        shape_path,
        index_path,
    )

    assert embeddings.shape == (3, 384)
    assert embeddings.dtype == np.float32
    assert news_index == index

    np.testing.assert_array_equal(
        np.asarray(embeddings),
        data,
    )