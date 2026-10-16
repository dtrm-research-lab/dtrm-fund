"""Synthetic link-shape evidence is not an authenticated link vintage."""
from __future__ import annotations

import pytest

from dtrm.phase4.legacy_matched_link_projection import (
    LegacyLinkProjectionError,
    preview_synthetic_legacy_links,
)


def test_two_known_string_fields_are_structural_only() -> None:
    r = preview_synthetic_legacy_links([
        {"ticker": "SYNTHETIC_TICKER", "match_type": "SYNTHETIC_CLASS"},
    ])
    assert r["source_link_count"] == 1
    assert r["engineering_status"] == "SYNTHETIC_LEGACY_LINK_SHAPE_PASS"
    assert r["match_type_semantics_authenticated"] is False
    assert r["confidence_available_or_inferred"] is False
    assert r["historical_link_first_seen_authenticated"] is False
    assert r["mapping_authenticated"] is False
    assert r["temporal_state_training_permitted"] is False
    assert r["model_fitting_permitted"] is False
    assert "SYNTHETIC_TICKER" not in repr(r)
    assert "SYNTHETIC_CLASS" not in repr(r)


@pytest.mark.parametrize("invalid", [
    {"ticker": 1, "match_type": "SYNTH"},
    {"ticker": "SYNTH", "match_type": 3.1},
    {"ticker": "SYNTH"},
    {"ticker": "", "match_type": "SYNTH"},
    {"ticker": " SYNTH", "match_type": "SYNTH"},
    {"ticker": "SYNTH", "match_type": ""},
])
def test_invalid_structural_fields_fail_closed(invalid: dict[str, object]) -> None:
    with pytest.raises(LegacyLinkProjectionError, match="INVALID_SYNTHETIC_LINK_SHAPE"):
        preview_synthetic_legacy_links([invalid])


def test_uninspected_fields_not_assumed_absent_or_authenticated() -> None:
    r = preview_synthetic_legacy_links([
        {"ticker": "SYNTHETIC", "match_type": "SYNTHETIC", "unknown_key": "X"}
    ])
    assert r["uninspected_extra_keys_present"] is True
    assert r["historical_content_first_seen_authenticated"] is False
    assert r["historical_link_first_seen_authenticated"] is False


def test_extra_value_never_enters_report() -> None:
    r = preview_synthetic_legacy_links([
        {"ticker": "SYNTHETIC", "match_type": "SYNTHETIC", "unknown_key": "PRIVATE"}
    ])
    assert "PRIVATE" not in repr(r)
    assert "unknown_key" not in repr(r)


def test_no_numerical_confidence_inferred_from_type_or_synthetic_label() -> None:
    r = preview_synthetic_legacy_links([
        {"ticker": "SYNTHETIC", "match_type": "0.999"}
    ])
    assert r["confidence_available_or_inferred"] is False
    assert "0.999" not in repr(r)


def test_empty_is_not_historical_zero() -> None:
    r = preview_synthetic_legacy_links([])
    assert r["source_link_count"] == 0
    assert r["historical_link_first_seen_authenticated"] is False
    assert r["temporal_state_training_permitted"] is False
    assert r["source_authenticated"] is False


def test_refuse_non_list_or_large_batch() -> None:
    for items in ("raw-source-values", list(range(10001))):
        with pytest.raises(LegacyLinkProjectionError, match="INVALID_SYNTHETIC_LINK_COUNT"):
            preview_synthetic_legacy_links(items)
