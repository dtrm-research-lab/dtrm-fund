from datetime import date

from dtrm.beta_alignment import beta_on_or_before


BETAS = [
    ("2026-01-05", 1.10),
    ("2026-01-08", 1.20),
    ("2026-01-12", 1.30),
]


def test_beta_on_or_before_exact_match():
    result = beta_on_or_before(
        BETAS,
        "2026-01-12",
        tolerance_days=20,
    )

    assert result == (date(2026, 1, 12), 1.30)


def test_beta_on_or_before_uses_latest_previous_beta():
    result = beta_on_or_before(
        BETAS,
        "2026-01-10",
        tolerance_days=20,
    )

    assert result == (date(2026, 1, 8), 1.20)


def test_beta_on_or_before_never_uses_future_beta():
    result = beta_on_or_before(
        BETAS,
        "2026-01-09",
        tolerance_days=20,
    )

    assert result == (date(2026, 1, 8), 1.20)


def test_beta_on_or_before_respects_tolerance():
    result = beta_on_or_before(
        [("2026-01-01", 1.10)],
        "2026-01-25",
        tolerance_days=20,
    )

    assert result is None


def test_beta_on_or_before_returns_none_without_previous_beta():
    result = beta_on_or_before(
        BETAS,
        "2026-01-01",
        tolerance_days=20,
    )

    assert result is None