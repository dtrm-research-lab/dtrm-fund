"""Phase IV frozen C0 static clock audit; no production data or prices."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.frozen_control_clock_static_audit import (
    BASE,
    FINDINGS,
    FROZEN_BLOBS,
    V5,
    V6,
    StaticClockAuditError,
    assess_frozen_control_clock,
    check_blobs,
    check_fragments,
    git_blob_sha1,
    load_fixed_frozen_sources,
    main,
)


def test_three_frozen_sources_match_registered_git_blobs() -> None:
    src = load_fixed_frozen_sources()
    assert set(src) == {V5, V6, BASE}
    for name, sha in FROZEN_BLOBS:
        assert git_blob_sha1(src[name]) == sha
    check_blobs(src)


def test_assessment_has_no_positive_scientific_gate(capsys) -> None:
    state = assess_frozen_control_clock(load_fixed_frozen_sources())
    report = state.to_json()
    assert report["engineering_status"] == "PASS_FROZEN_CONTROL_STATIC_CLOCK_AUDIT"
    assert report["scientific_status"] == "BLOCKED_CONTROL_CLOCK_ATTESTATION"
    assert tuple(report["findings"]) == FINDINGS
    for key in (
        "historical_leakage_proven",
        "source_authenticated",
        "decision_clock_bound",
        "control_clock_authenticated",
        "model_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
    ):
        assert report[key] is False
    assert main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output == report
    assert set(output) == set(report)


def test_immutable_domain_and_detached_serialization() -> None:
    state = assess_frozen_control_clock(load_fixed_frozen_sources())
    with pytest.raises(FrozenInstanceError):
        state.findings = ()
    report = state.to_json()
    report["findings"].clear()
    report["frozen_blobs"][0]["git_blob_sha1"] = "wrong"
    report["source_authenticated"] = True
    assert state.to_json()["source_authenticated"] is False
    assert state.to_json()["findings"] == list(FINDINGS)
    assert state.frozen_blobs == FROZEN_BLOBS


@pytest.mark.parametrize("name", (V5, V6, BASE))
def test_frozen_code_mutation_fails(name: str) -> None:
    changed = load_fixed_frozen_sources()
    changed[name] += b"\n# synthetic tamper attempt\n"
    with pytest.raises(StaticClockAuditError, match="BLOCKED_FROZEN_CONTROL_SOURCE_DRIFT"):
        assess_frozen_control_clock(changed)


@pytest.mark.parametrize("name", (V5, V6, BASE))
def test_missing_source_fails(name: str) -> None:
    missing = load_fixed_frozen_sources()
    del missing[name]
    with pytest.raises(StaticClockAuditError):
        check_blobs(missing)


def test_additional_source_fails() -> None:
    extra = load_fixed_frozen_sources()
    extra["research/local_data/secret.pkl"] = b"nope"
    with pytest.raises(StaticClockAuditError):
        check_blobs(extra)


@pytest.mark.parametrize("name,required", (
    (V5, b'event_date = pd.to_datetime(str(raw_date)[:10], utc=True)'),
    (V5, b'if _naive_utc(date) <= cutoff:'),
    (V6, b'beta_pre = v5.beta_pre_for_pairs(pairs, prices)'),
    (BASE, b'frame["close"]'),
))
def test_missing_semantic_fragment_fails_closed(name: str, required: bytes) -> None:
    data = load_fixed_frozen_sources()
    assert required in data[name]
    data[name] = data[name].replace(required, b"synthetic_invalid_clock_claim", 1)
    with pytest.raises(StaticClockAuditError):
        check_fragments(data)


def test_fixed_loader_never_opens_arbitrary_path(monkeypatch) -> None:
    original = Path.read_bytes
    seen: list[str] = []

    def tracked_read(path: Path) -> bytes:
        seen.append(str(path))
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", tracked_read)
    assert len(load_fixed_frozen_sources()) == 3
    assert len(seen) == 3
    assert all(path.endswith(".py") for path in seen)
    assert all("/research/experiments/" in path for path in seen)
