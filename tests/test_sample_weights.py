import numpy as np
import pytest

from dtrm.sample_weights import legacy_news_weights


def test_legacy_news_weights():
    weights = legacy_news_weights(
        ["n1", "n1", "n2", "n3", "n3", "n3"]
    )

    np.testing.assert_allclose(
        weights,
        [
            0.5,
            0.5,
            1.0,
            1.0 / 3.0,
            1.0 / 3.0,
            1.0 / 3.0,
        ],
    )


def test_each_news_id_has_total_weight_one():
    news_ids = ["n1", "n1", "n2", "n3", "n3", "n3"]
    weights = legacy_news_weights(news_ids)

    totals = {}

    for news_id, weight in zip(news_ids, weights):
        totals[news_id] = totals.get(news_id, 0.0) + float(weight)

    assert totals["n1"] == pytest.approx(1.0)
    assert totals["n2"] == pytest.approx(1.0)
    assert totals["n3"] == pytest.approx(1.0)


def test_empty_input_returns_empty_array():
    weights = legacy_news_weights([])

    assert weights.size == 0
    assert weights.dtype == np.float32