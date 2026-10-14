"""Phase IV: offline, frozen Phase-III/C0 clock *static* audit only.

This module never imports the frozen builders or reads data caches and cannot
authenticate any real observation/price clock or authorize model execution.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

FROZEN_BLOBS: tuple[tuple[str, str], ...] = (
    ("research/experiments/build_phase3_mm1_v5_exante_artifacts.py",
     "75b2c07e86820923deaaebc1d8c4b4265db7d877"),
    ("research/experiments/build_phase3_mm1_v6_exante_artifacts.py",
     "0b4a2d61715ba6d3dc497118a98a5aa48e765f42"),
    ("research/experiments/run_exante_baseline_v0.py",
     "cecd1a71ffc1526d64f37d0a52b47db4b1e36675"),
)

V5 = FROZEN_BLOBS[0][0]
V6 = FROZEN_BLOBS[1][0]
BASE = FROZEN_BLOBS[2][0]

# Exact inherited source fragments: fingerprints of *static* code only.
# They do not independently demonstrate when real-world information arrived.
REQUIRED_FRAGMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (V5, (
        'event_date = pd.to_datetime(str(raw_date)[:10], utc=True)',
        'if _naive_utc(date) <= cutoff:',
        'stock_history = price_history_on_or_before(prices[ticker], event_date)',
        'market_history = price_history_on_or_before(prices["SPY"], event_date)',
    )),
    (V6, (
        'event_date = pd.to_datetime(str(raw_date)[:10], utc=True)',
        'prices = v5.load_exante_price_cache()',
        'beta_pre = v5.beta_pre_for_pairs(pairs, prices)',
        '{"text": 1, "date": 1, "matched_tickers": 1}',
    )),
    (BASE, (
        'for path in PRICE_CACHE.glob("*_2026-07-05.pkl"):',
        'frame["date"]',
        'frame["close"]',
    )),
)

FINDINGS = (
    "FROZEN_NEWS_DATE_TRUNCATED_TO_CALENDAR_DAY",
    "PRICE_HISTORY_FILTERS_BY_DATE_NOT_AUTHENTICATED_PRICE_ARRIVAL",
    "V6_REUSES_FROZEN_BETA_AND_PRICE_CACHE",
    "CURRENT_CODE_ALONE_CANNOT_ATTEST_OBSERVATION_VINTAGE_OR_LINK_TIME",
)


class StaticClockAuditError(ValueError):
    """Fixed fail-closed error; no content, path, secrets, or actual data."""


def git_blob_sha1(content: bytes) -> str:
    """Calculate Git's blob object hash of bytes, independent of Git checkout."""
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + b"\x00" + content
    ).hexdigest()


def _fail() -> None:
    raise StaticClockAuditError("BLOCKED_FROZEN_CONTROL_SOURCE_DRIFT")


def check_blobs(source_bytes: Mapping[str, bytes]) -> None:
    """Require exactly the three frozen, original source blobs."""
    if not isinstance(source_bytes, Mapping) or set(source_bytes) != {p for p, _ in FROZEN_BLOBS}:
        _fail()
    for path, expected in FROZEN_BLOBS:
        content = source_bytes[path]
        if type(content) is not bytes or git_blob_sha1(content) != expected:
            _fail()


def check_fragments(source_bytes: Mapping[str, bytes]) -> None:
    """Recognize documented code properties; do not import/execute the source."""
    for path, expected in REQUIRED_FRAGMENTS:
        try:
            content = source_bytes[path].decode("utf-8")
        except (KeyError, AttributeError, UnicodeError):
            _fail()
        for fragment in expected:
            if fragment not in content:
                _fail()


@dataclass(frozen=True, slots=True)
class StaticClockAssessment:
    """Immutable non-promotable snapshot of source-code observations."""

    frozen_blobs: tuple[tuple[str, str], ...]
    findings: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        """Create detached JSON values, preserving permanently blocked flags."""
        return {
            "schema_version": "dtrm.phase4.frozen_control_clock_static.v0",
            "engineering_status": "PASS_FROZEN_CONTROL_STATIC_CLOCK_AUDIT",
            "scientific_status": "BLOCKED_CONTROL_CLOCK_ATTESTATION",
            "historical_leakage_proven": False,
            "source_authenticated": False,
            "decision_clock_bound": False,
            "control_clock_authenticated": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "frozen_blobs": [
                {"path": path, "git_blob_sha1": sha} for path, sha in self.frozen_blobs
            ],
            "findings": list(self.findings),
        }


def assess_frozen_control_clock(source_bytes: Mapping[str, bytes]) -> StaticClockAssessment:
    """Pure fail-closed static observation graph. No third-party I/O."""
    check_blobs(source_bytes)
    check_fragments(source_bytes)
    return StaticClockAssessment(frozen_blobs=FROZEN_BLOBS, findings=FINDINGS)


def load_fixed_frozen_sources() -> dict[str, bytes]:
    """Read *only* fixed tracked Python sources, not any pickle/news/cache."""
    repository = Path(__file__).resolve().parents[3]
    result: dict[str, bytes] = {}
    for path, _ in FROZEN_BLOBS:
        target = repository / path
        if not target.is_file() or target.is_symlink():
            _fail()
        try:
            result[path] = target.read_bytes()
        except OSError:
            _fail()
    return result


def main() -> int:
    try:
        state = assess_frozen_control_clock(load_fixed_frozen_sources())
    except (StaticClockAuditError, OSError, TypeError):
        print("BLOCKED_FROZEN_CONTROL_SOURCE_DRIFT")
        return 2
    print(json.dumps(state.to_json(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
