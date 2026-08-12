from datetime import date

from dtrm.feature_windows import trailing_feature_window
from dtrm.target_windows import forward_target_window


def test_features_do_not_extend_beyond_prediction_time():
    event_date = date(2026, 1, 15)

    _, feature_end = trailing_feature_window(
        event_date,
        lookback_days=60,
    )

    target_start, _ = forward_target_window(
        event_date,
        horizon_days=60,
    )

    assert feature_end <= event_date
    assert target_start == event_date


def test_feature_and_target_windows_do_not_overlap_future_information():
    event_date = date(2026, 1, 15)

    _, feature_end = trailing_feature_window(
        event_date,
        lookback_days=60,
    )

    target_start, _ = forward_target_window(
        event_date,
        horizon_days=60,
    )

    assert feature_end <= target_start