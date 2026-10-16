"""Synthetic-only bridge for two-string legacy link structure.

Source shape observed by an *operator-held* audit is not a historical first-link clock.
Never accepts real Mongo, AWS, source, or protected outcome access. No raw values
are emitted: the canonical projection digest is solely an engineering identity.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "dtrm.phase4.legacy_link_projection_synthetic.v0"
LINK_KEYS = ("ticker", "match_type")


class LegacyLinkProjectionError(ValueError):
    """Fixed non-sensitive rejection reason."""


def _field(record: Mapping[str, Any], name: str) -> str:
    value = record.get(name)
    if not isinstance(value, str) or not 0 < len(value) <= 256:
        raise LegacyLinkProjectionError("INVALID_SYNTHETIC_LINK_SHAPE")
    if not value.strip() or value != value.strip():
        raise LegacyLinkProjectionError("INVALID_SYNTHETIC_LINK_SHAPE")
    return value


def preview_synthetic_legacy_links(
    projected_links: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """Profile *only* synthetic object shapes; no inference about extra keys.

    This method is deliberately unable to infer linked_at, first_seen, mapping
    trust, confidence or temporal history admissibility. It is NOT a real
    collector or safe way to reconstruct a timestamp for historical links.
    """
    if isinstance(projected_links, (str, bytes)) or not isinstance(
        projected_links, (tuple, list)
    ) or len(projected_links) > 10000:
        raise LegacyLinkProjectionError("INVALID_SYNTHETIC_LINK_COUNT")
    serialized: list[dict[str, str]] = []
    extra_fields_observed = False
    for item in projected_links:
        if not isinstance(item, Mapping):
            raise LegacyLinkProjectionError("INVALID_SYNTHETIC_LINK_SHAPE")
        projected = {name: _field(item, name) for name in LINK_KEYS}
        if set(item) - set(LINK_KEYS):
            extra_fields_observed = True
        serialized.append(projected)
    exact_bytes = json.dumps(
        serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return {
        "schema_version": SCHEMA,
        "dataset_role": "synthetic_only",
        "engineering_status": "SYNTHETIC_LEGACY_LINK_SHAPE_PASS",
        "source_link_count": len(serialized),
        "canonical_two_string_projection_sha256": hashlib.sha256(
            exact_bytes
        ).hexdigest(),
        "uninspected_extra_keys_present": extra_fields_observed,
        "match_type_semantics_authenticated": False,
        "confidence_available_or_inferred": False,
        "historical_link_first_seen_authenticated": False,
        "historical_content_first_seen_authenticated": False,
        "source_authenticated": False,
        "mapping_authenticated": False,
        "temporal_state_training_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
    }
