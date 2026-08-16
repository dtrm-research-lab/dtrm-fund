import pickle

import numpy as np

from dtrm.embedding_cache import load_legacy_embedding_cache
from dtrm.embedding_cache import embeddings_for_news_ids


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

def test_embeddings_for_news_ids_preserves_requested_order():
    embeddings = np.arange(
        4 * 384,
        dtype=np.float32,
    ).reshape(4, 384)

    news_index = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
    }

    result = embeddings_for_news_ids(
        embeddings,
        news_index,
        ["c", "a", "d"],
    )

    assert result.shape == (3, 384)
    assert result.dtype == np.float32

    np.testing.assert_array_equal(result[0], embeddings[2])
    np.testing.assert_array_equal(result[1], embeddings[0])
    np.testing.assert_array_equal(result[2], embeddings[3])