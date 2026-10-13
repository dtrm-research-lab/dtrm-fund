"""Pure synthetic-only v3 dispatch-envelope compatibility boundary.

A valid signature over caller-supplied bytes does not attest AWS origin or permit
scientific counting. The caller must not confuse a locally calculated digest with
independent source provenance.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
from datetime import UTC, date, datetime, time, timedelta
from typing import Never, cast

SCHEMA = "dtrm.phase4.repository_dispatch_envelope.v1"
EVENT_TYPE = "phase4_fmp_news_temporal_capture_v3"
ALGORITHM = "hmac-sha256"
MAX_BYTES = 16 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,256}$")
SLOT_CLOCKS = ((0, 15), (6, 15), (12, 15), (18, 15))
ENVELOPE_FIELDS = frozenset(
    {
        "schema_version",
        "campaign_statement",
        "campaign_statement_sha256",
        "target_slot",
        "target_at_utc",
        "dispatch_id",
        "dispatch_at_utc",
        "scheduler_identity",
        "signature_algorithm",
        "signature_key_id",
        "signature",
    }
)


class SyntheticV3EnvelopeError(ValueError):
    """Fixed-code failure, without echoing source values or cryptographic keys."""


def _bad(code: str) -> Never:
    raise SyntheticV3EnvelopeError(code)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _bad("INVALID_JSON")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    _bad("INVALID_JSON")


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        _bad("INVALID_JSON")
    return parsed


def _canonical(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _utc_string(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _bad("INVALID_CLOCK")
    if value.utcoffset() != timedelta(0):
        _bad("INVALID_CLOCK")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        _bad("INVALID_CLOCK")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _bad("INVALID_CLOCK")
    if _utc_string(parsed) != value:
        _bad("INVALID_CLOCK")
    return parsed


def _require_identifier(value: object) -> str:
    if not isinstance(value, str) or IDENTIFIER_RE.fullmatch(value) is None:
        _bad("INVALID_IDENTITY")
    return value


def _require_sha256(value: object) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _bad("INVALID_DIGEST")
    return value


def _target_at(start_day: date, slot: int) -> datetime:
    if type(start_day) is not date or type(slot) is not int or not 0 <= slot < 56:
        _bad("INVALID_TARGET")
    hour, minute = SLOT_CLOCKS[slot % 4]
    return datetime.combine(start_day, time(hour, minute, tzinfo=UTC)) + timedelta(
        days=slot // 4
    )


def check_synthetic_signed_dispatch(
    *,
    envelope_bytes: bytes,
    expected_envelope_sha256: str,
    activation_id: str,
    activation_sha256: str,
    scheduler_identity: str,
    key_id: str,
    hmac_key: bytes,
    start_utc_day: date,
    target_slot: int,
    run_attempt: int,
    runner_started_utc: datetime,
) -> dict[str, object]:
    """Verify a local signed envelope's wire compatibility; never attest origin."""
    if (
        type(envelope_bytes) is not bytes
        or not envelope_bytes
        or len(envelope_bytes) > MAX_BYTES
    ):
        _bad("INVALID_ENVELOPE_BYTES")
    if type(hmac_key) is not bytes or not 32 <= len(hmac_key) <= 4096:
        _bad("INVALID_AUTHORITY")
    if type(run_attempt) is not int or run_attempt != 1:
        _bad("INVALID_RUN_ATTEMPT")
    if type(runner_started_utc) is not datetime:
        _bad("INVALID_CLOCK")
    _utc_string(runner_started_utc)
    expected_target = _target_at(start_utc_day, target_slot)
    _require_identifier(activation_id)
    _require_sha256(activation_sha256)
    _require_identifier(scheduler_identity)
    _require_identifier(key_id)
    expected_sha = _require_sha256(expected_envelope_sha256)
    if not hmac.compare_digest(
        hashlib.sha256(envelope_bytes).hexdigest(), expected_sha
    ):
        _bad("ENVELOPE_DIGEST_MISMATCH")

    try:
        parsed = json.loads(
            envelope_bytes.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except SyntheticV3EnvelopeError:
        raise
    except (UnicodeError, ValueError, RecursionError):
        _bad("INVALID_JSON")
    if not isinstance(parsed, dict) or frozenset(parsed) != ENVELOPE_FIELDS:
        _bad("INVALID_ENVELOPE_SCHEMA")
    payload = cast(dict[str, object], parsed)
    if _canonical(payload) != envelope_bytes:
        _bad("NONCANONICAL_JSON")
    if (
        payload["schema_version"] != SCHEMA
        or payload["signature_algorithm"] != ALGORITHM
    ):
        _bad("INVALID_ENVELOPE_SCHEMA")
    if (
        payload["campaign_statement"] != activation_id
        or payload["campaign_statement_sha256"] != activation_sha256
        or payload["scheduler_identity"] != scheduler_identity
        or payload["signature_key_id"] != key_id
    ):
        _bad("AUTHORITY_BINDING_MISMATCH")
    if type(payload["target_slot"]) is not int or payload["target_slot"] != target_slot:
        _bad("TARGET_SLOT_MISMATCH")
    target_time = _parse_utc(payload["target_at_utc"])
    if target_time != expected_target:
        _bad("TARGET_CLOCK_MISMATCH")
    dispatch_time = _parse_utc(payload["dispatch_at_utc"])
    expected_id = hashlib.sha256(
        _canonical(
            {
                "campaign_statement": activation_id,
                "campaign_statement_sha256": activation_sha256,
                "target_at_utc": _utc_string(expected_target),
                "target_slot": target_slot,
            }
        )
    ).hexdigest()
    if not hmac.compare_digest(_require_sha256(payload["dispatch_id"]), expected_id):
        _bad("DISPATCH_ID_MISMATCH")
    signature = _require_sha256(payload["signature"])
    signed = {name: value for name, value in payload.items() if name != "signature"}
    computed = hmac.new(hmac_key, _canonical(signed), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        _bad("SIGNATURE_MISMATCH")
    if (
        not expected_target
        <= dispatch_time
        <= runner_started_utc
        <= (expected_target + timedelta(minutes=120))
    ):
        _bad("START_WINDOW_MISMATCH")
    return {
        "schema_version": "dtrm.phase4.v3_signed_dispatch_synthetic_boundary.v0",
        "status": "SYNTHETIC_COMPATIBILITY_ONLY",
        "target_slot": target_slot,
        "synthetic_input_only": True,
        "cryptographic_test_passed": True,
        "scheduler_origin_independently_verified": False,
        "runtime_provenance_independently_verified": False,
        "dynamodb_claim_independently_verified": False,
        "scientific_counting_permitted": False,
        "provider_access_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "phase3_policy_mutation_permitted": False,
    }
