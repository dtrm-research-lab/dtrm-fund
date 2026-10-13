"""Synthetic-only wire-compatibility tests for the v3 signed dispatch envelope."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

import pytest

from dtrm.phase4.v3_signed_dispatch_synthetic_boundary import (
    SyntheticV3EnvelopeError,
    _target_at,
    check_synthetic_signed_dispatch,
)

_KEY = b"synthetic-only-hmac-key-not-for-production!"[:32]
_ID = "synthetic-campaign-v3"
_DIGEST = "a" * 64
_SCHEDULER = "synthetic-scheduler"
_KEY_ID = "synthetic-key-v0"
_START = date(2026, 11, 1)
_CLOCKS = ((0, 15), (6, 15), (12, 15), (18, 15))
_GATES = (
    "scheduler_origin_independently_verified",
    "runtime_provenance_independently_verified",
    "dynamodb_claim_independently_verified",
    "scientific_counting_permitted",
    "provider_access_permitted",
    "outcome_access_permitted",
    "mm1_execution_permitted",
    "temporal_state_outcome_fitting_permitted",
    "phase3_policy_mutation_permitted",
)


def _canonical(data: dict[str, object]) -> bytes:
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def _target(slot: int) -> datetime:
    hour, minute = _CLOCKS[slot % 4]
    return datetime.combine(_START, time(hour, minute, tzinfo=UTC)) + timedelta(
        days=slot // 4
    )


def _signed_wire(
    *,
    slot: int = 0,
    dispatch_delta: timedelta = timedelta(seconds=1),
    payload_changes: dict[str, object] | None = None,
) -> bytes:
    target = _target(slot)
    identifier = {
        "campaign_statement": _ID,
        "campaign_statement_sha256": _DIGEST,
        "target_at_utc": target.isoformat().replace("+00:00", "Z"),
        "target_slot": slot,
    }
    payload: dict[str, object] = {
        "schema_version": "dtrm.phase4.repository_dispatch_envelope.v1",
        **identifier,
        "dispatch_id": hashlib.sha256(_canonical(identifier)).hexdigest(),
        "dispatch_at_utc": (target + dispatch_delta).isoformat().replace("+00:00", "Z"),
        "scheduler_identity": _SCHEDULER,
        "signature_algorithm": "hmac-sha256",
        "signature_key_id": _KEY_ID,
    }
    if payload_changes is not None:
        payload.update(payload_changes)
    payload["signature"] = hmac.new(
        _KEY, _canonical(payload), hashlib.sha256
    ).hexdigest()
    return _canonical(payload)


def _check(
    *,
    wire: bytes | None = None,
    slot: int = 0,
    runner_delta: timedelta = timedelta(seconds=3),
    **overrides: Any,
) -> dict[str, object]:
    if wire is None:
        wire = _signed_wire(slot=slot)
    params: dict[str, Any] = {
        "envelope_bytes": wire,
        "expected_envelope_sha256": hashlib.sha256(wire).hexdigest(),
        "activation_id": _ID,
        "activation_sha256": _DIGEST,
        "scheduler_identity": _SCHEDULER,
        "key_id": _KEY_ID,
        "hmac_key": _KEY,
        "start_utc_day": _START,
        "target_slot": slot,
        "run_attempt": 1,
        "runner_started_utc": _target(slot) + runner_delta,
    }
    params.update(overrides)
    return check_synthetic_signed_dispatch(**params)


@pytest.mark.parametrize("slot", (0, 1, 2, 3, 52, 55))
def test_valid_registered_slot_clocks_are_synthetic_only(slot: int) -> None:
    result = _check(slot=slot)
    assert result["status"] == "SYNTHETIC_COMPATIBILITY_ONLY"
    assert result["target_slot"] == slot
    assert result["cryptographic_test_passed"] is True
    assert result["synthetic_input_only"] is True
    assert all(result[flag] is False for flag in _GATES)
    assert "signature" not in result
    assert "hmac_key" not in result


def test_120_minute_boundary_is_inclusive_without_early_release() -> None:
    wire = _signed_wire(dispatch_delta=timedelta(minutes=120))
    report = _check(wire=wire, runner_delta=timedelta(minutes=120))
    assert report["scientific_counting_permitted"] is False


@pytest.mark.parametrize(
    ("changes", "error"),
    (
        ({"campaign_statement": "wrong"}, "AUTHORITY_BINDING_MISMATCH"),
        ({"campaign_statement_sha256": "b" * 64}, "AUTHORITY_BINDING_MISMATCH"),
        ({"scheduler_identity": "bad-scheduler"}, "AUTHORITY_BINDING_MISMATCH"),
        ({"signature_key_id": "bad-key"}, "AUTHORITY_BINDING_MISMATCH"),
        ({"target_slot": 1}, "TARGET_SLOT_MISMATCH"),
        ({"target_at_utc": "2026-11-01T06:15:00Z"}, "TARGET_CLOCK_MISMATCH"),
        ({"dispatch_id": "b" * 64}, "DISPATCH_ID_MISMATCH"),
        ({"signature_algorithm": "other"}, "INVALID_ENVELOPE_SCHEMA"),
        ({"schema_version": "v2"}, "INVALID_ENVELOPE_SCHEMA"),
        ({"extra_field": 1}, "INVALID_ENVELOPE_SCHEMA"),
    ),
)
def test_changed_authenticated_fields_never_count(
    changes: dict[str, object], error: str
) -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match=f"^{error}$"):
        _check(wire=_signed_wire(payload_changes=changes))


@pytest.mark.parametrize(
    ("wire", "error"),
    (
        (b"", "INVALID_ENVELOPE_BYTES"),
        (b"x" * 17000, "INVALID_ENVELOPE_BYTES"),
        (b"not-json", "INVALID_JSON"),
        (b'{"signature":NaN}', "INVALID_JSON"),
        (b'{"signature":1,"signature":2}', "INVALID_JSON"),
    ),
)
def test_invalid_wire_bytes_fail_closed(wire: bytes, error: str) -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match=f"^{error}$"):
        _check(wire=wire)


@pytest.mark.parametrize(
    "wire",
    (
        b'{"overflow":1e999}',
        b'{"overflow":-1e999}',
        b'{"overflow":1e309}',
    ),
)
def test_json_exponent_overflow_produces_fixed_error(wire: bytes) -> None:
    # Digest intentionally matches the exact malformed synthetic bytes.
    with pytest.raises(SyntheticV3EnvelopeError, match="^INVALID_JSON$"):
        _check(wire=wire)


def test_noncanonical_bytes_fail_closed() -> None:
    payload = json.loads(_signed_wire())
    wire = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    with pytest.raises(SyntheticV3EnvelopeError, match="^NONCANONICAL_JSON$"):
        _check(wire=wire)


def test_wrong_independent_digest_mismatch() -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match="^ENVELOPE_DIGEST_MISMATCH$"):
        _check(expected_envelope_sha256="0" * 64)


def test_invalid_signature_and_wrong_key_fail_closed() -> None:
    payload = json.loads(_signed_wire())
    payload["signature"] = "0" * 64
    with pytest.raises(SyntheticV3EnvelopeError, match="^SIGNATURE_MISMATCH$"):
        _check(wire=_canonical(payload))
    with pytest.raises(SyntheticV3EnvelopeError, match="^SIGNATURE_MISMATCH$"):
        _check(hmac_key=b"Z" * 32)


@pytest.mark.parametrize(
    ("dispatch_delta", "runner_delta"),
    (
        (timedelta(seconds=-1), timedelta(seconds=5)),
        (timedelta(seconds=6), timedelta(seconds=5)),
        (timedelta(minutes=121), timedelta(minutes=121)),
        (timedelta(seconds=1), timedelta(minutes=121)),
    ),
)
def test_dispatch_and_runner_clock_fail_closed(
    dispatch_delta: timedelta, runner_delta: timedelta
) -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match="^START_WINDOW_MISMATCH$"):
        _check(
            wire=_signed_wire(dispatch_delta=dispatch_delta),
            runner_delta=runner_delta,
        )


@pytest.mark.parametrize(
    ("changes", "error"),
    (
        ({"run_attempt": 2}, "INVALID_RUN_ATTEMPT"),
        ({"run_attempt": True}, "INVALID_RUN_ATTEMPT"),
        ({"target_slot": 56}, "INVALID_TARGET"),
        ({"target_slot": -1}, "INVALID_TARGET"),
        ({"target_slot": True}, "INVALID_TARGET"),
        ({"hmac_key": b"x" * 10}, "INVALID_AUTHORITY"),
        ({"start_utc_day": datetime(2026, 11, 1, tzinfo=UTC)}, "INVALID_TARGET"),
        ({"runner_started_utc": datetime(2026, 11, 1)}, "INVALID_CLOCK"),
    ),
)
def test_noncanonical_arguments_fail_closed(
    changes: dict[str, object], error: str
) -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match=f"^{error}$"):
        _check(**changes)


@pytest.mark.parametrize("slot", (0, 55))
def test_unrepresentable_14_day_window_fails_even_for_first_slot(slot: int) -> None:
    with pytest.raises(SyntheticV3EnvelopeError, match="^INVALID_TARGET$"):
        _check(slot=slot, start_utc_day=date.max)


def test_full_window_exact_maximum_representable_start_day() -> None:
    assert _target_at(date(9999, 12, 18), 55) == datetime(
        9999, 12, 31, 18, 15, tzinfo=UTC
    )
    with pytest.raises(SyntheticV3EnvelopeError, match="^INVALID_TARGET$"):
        _target_at(date(9999, 12, 19), 0)


def test_synthetic_results_deterministic_and_noncounting() -> None:
    assert _check(slot=55) == _check(slot=55)
    assert all(_check(slot=55)[flag] is False for flag in _GATES)
