import pytest

from dtrm.legacy_features import legacy_ret_spy_evt_feature


def test_legacy_ret_spy_evt_feature():
    market_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 110.0),
    ]

    result = legacy_ret_spy_evt_feature(
        market_prices=market_prices,
        event_date="2026-01-15",
        horizon_days=60,
        tolerance_days=5,
    )

    assert result == pytest.approx(0.10)


def test_legacy_ret_spy_evt_changes_with_future_price():
    base_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 110.0),
    ]

    changed_future_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 130.0),
    ]

    base_result = legacy_ret_spy_evt_feature(
        base_prices,
        event_date="2026-01-15",
    )

    changed_result = legacy_ret_spy_evt_feature(
        changed_future_prices,
        event_date="2026-01-15",
    )

    assert base_result == pytest.approx(0.10)
    assert changed_result == pytest.approx(0.30)
    assert changed_result != base_result
    