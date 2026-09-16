from __future__ import annotations

from pathlib import Path

from dtrm.phase4.prospective_activation_package import (
    ACTIVATION_STATEMENT_ID,
    EARLIEST_FINALIZATION_UTC,
    FIRST_SLOT_UTC,
    LAST_SLOT_UTC,
    PROSPECTIVE_START_UTC,
    ProspectiveActivationPackageError,
    verify_package,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = ROOT / "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2.json"
PACKAGE = ROOT / "research/evidence/phase4_prospective_activation_package_v1.json"

STATEMENT_SHA256 = "540a46f4b80e73cb776596936fd2d30fdf7d74d8a64d2c6ed2bd565deb8ed2b1"
PACKAGE_SHA256 = "25f05705690c28054919963a0204703344da6dada29a497215ad3317abdce288"


def test_prepared_activation_package_is_exact_and_source_value_free() -> None:
    verified = verify_package(
        statement_bytes=STATEMENT.read_bytes(),
        package_bytes=PACKAGE.read_bytes(),
    )
    assert verified.statement_sha256 == STATEMENT_SHA256
    assert verified.package_sha256 == PACKAGE_SHA256


def test_campaign_window_is_frozen_before_slot_zero() -> None:
    assert ACTIVATION_STATEMENT_ID == "phase4-prospective-capture-2026-09-18-v1"
    assert PROSPECTIVE_START_UTC == "2026-09-18T00:00:00Z"
    assert FIRST_SLOT_UTC == "2026-09-18T00:15:00Z"
    assert LAST_SLOT_UTC == "2026-10-01T18:15:00Z"
    assert EARLIEST_FINALIZATION_UTC == "2026-10-01T22:15:00Z"


def test_tampering_fails_closed() -> None:
    statement = STATEMENT.read_bytes().replace(
        b'"periodic_capture_activation_permitted": true',
        b'"periodic_capture_activation_permitted": false',
    )
    try:
        verify_package(statement_bytes=statement, package_bytes=PACKAGE.read_bytes())
    except ProspectiveActivationPackageError:
        pass
    else:
        raise AssertionError("tampered activation statement must fail closed")
