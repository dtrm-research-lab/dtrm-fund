"""Acceptance tests for the synthetic prospective-capture protocol graph."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.prospective_capture import (
    BINDING_PATH,
    BINDING_SHA256,
    PROTOCOL_PATH,
    PROTOCOL_SHA256,
    ProspectiveCaptureError,
    expected_version_id,
    normalize_capture_bundle,
    run_prospective_capture_review,
    serialize_capture_review,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase4_prospective_capture_bundle_v0.json"
REPORT = ROOT / "research/reports/DTRM_PHASE4_PROSPECTIVE_CAPTURE_SYNTHETIC_V0.json"


@pytest.fixture
def payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _records(payload: dict[str, object]) -> list[dict[str, object]]:
    return payload["records"]  # type: ignore[return-value]


def _run(payload: dict[str, object]) -> dict[str, object]:
    return payload["run"]  # type: ignore[return-value]


def _collector(payload: dict[str, object]) -> dict[str, object]:
    return payload["collector"]  # type: ignore[return-value]


def test_valid_bundle_is_aggregate_only_and_scientifically_blocked(payload):
    result = run_prospective_capture_review(payload).to_dict()
    assert result["engineering_status"] == (
        "PASS_SYNTHETIC_PROSPECTIVE_CAPTURE_PROTOCOL"
    )
    assert result["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"
    assert result["counts"] == {
        "record_count": 3,
        "logical_event_count": 2,
        "asset_link_count": 4,
    }
    for field in (
        "source_authenticated",
        "collector_deployed",
        "clock_authenticated",
        "coverage_authenticated",
        "history_construction_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
    ):
        assert result[field] is False
    encoded = serialize_capture_review(run_prospective_capture_review(payload))
    assert "provider-event-001" not in encoded
    assert '"ticker"' not in encoded


def test_normalized_state_is_frozen_and_detached(payload):
    bundle = normalize_capture_bundle(payload)
    with pytest.raises(FrozenInstanceError):
        bundle.run.run_id = "changed"
    _run(payload)["run_id"] = "changed"
    assert bundle.run.run_id == "00000000-0000-4000-8000-000000000001"


def test_record_and_link_input_order_do_not_change_output(payload):
    expected = serialize_capture_review(run_prospective_capture_review(payload))
    _records(payload).reverse()
    for record in _records(payload):
        links = record["asset_links"]
        assert isinstance(links, list)
        links.reverse()
    assert serialize_capture_review(run_prospective_capture_review(payload)) == expected


def test_timezone_equivalents_normalize_before_hash_validation(payload):
    _run(payload)["started_at"] = "2026-09-10T12:00:00+02:00"
    _run(payload)["response_received_at"] = "2026-09-10T12:01:00+02:00"
    _run(payload)["completed_at"] = "2026-09-10T12:05:00+02:00"
    for record in _records(payload):
        record["version_observed_at"] = "2026-09-10T12:01:00+02:00"
        record["first_seen_at"] = "2026-09-10T12:01:00+02:00"
        links = record["asset_links"]
        assert isinstance(links, list)
        for link in links:
            assert isinstance(link, dict)
            link["linked_at"] = str(link["linked_at"]).replace(
                "T10:", "T12:"
            ).replace("Z", "+02:00")
    assert run_prospective_capture_review(payload).run.to_dict()["started_at"] == (
        "2026-09-10T10:00:00Z"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("started_at", "2026-09-10T10:02:00Z"),
        ("response_received_at", "2026-09-10T10:06:00Z"),
        ("completed_at", "2026-09-10T10:00:59Z"),
        ("started_at", "2026-09-10T10:00:00"),
    ],
)
def test_run_clock_boundary_fails_closed(payload, field, value):
    _run(payload)[field] = value
    with pytest.raises(ProspectiveCaptureError, match="clock|instant"):
        run_prospective_capture_review(payload)


def test_equal_run_clock_boundaries_are_allowed_for_zero_version_run(payload):
    _run(payload).update(
        {
            "started_at": "2026-09-10T10:00:00Z",
            "response_received_at": "2026-09-10T10:00:00Z",
            "completed_at": "2026-09-10T10:00:00Z",
            "observed_candidates": 0,
            "new_versions": 0,
            "repeat_sightings": 0,
            "rejected_candidates": 0,
        }
    )
    payload["records"] = []
    result = run_prospective_capture_review(payload)
    assert result.output_ledger_head_sha256 is None


@pytest.mark.parametrize("bad", [True, -1, 1.5, "1"])
def test_candidate_counters_require_nonnegative_integers(payload, bad):
    _run(payload)["repeat_sightings"] = bad
    with pytest.raises(ProspectiveCaptureError, match="count"):
        run_prospective_capture_review(payload)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("observed_candidates", 6, "do not reconcile"),
        ("new_versions", 2, "does not match records"),
    ],
)
def test_candidate_counters_reconcile(payload, field, value, message):
    _run(payload)[field] = value
    if field == "new_versions":
        _run(payload)["observed_candidates"] = 4
    with pytest.raises(ProspectiveCaptureError, match=message):
        run_prospective_capture_review(payload)


def test_non_genesis_zero_version_run_preserves_prior_head(payload):
    prior = "a" * 64
    payload["previous_ledger_head_sha256"] = prior
    payload["records"] = []
    _run(payload).update(
        {
            "observed_candidates": 2,
            "new_versions": 0,
            "repeat_sightings": 1,
            "rejected_candidates": 1,
        }
    )
    result = run_prospective_capture_review(payload)
    assert result.input_ledger_head_sha256 == prior
    assert result.output_ledger_head_sha256 == prior


def test_version_id_is_derived_from_logical_identity_and_content(payload):
    record = _records(payload)[0]
    assert record["version_id"] == expected_version_id(
        str(record["source_event_id"]), str(record["content_sha256"])
    )
    record["version_id"] = "0" * 64
    with pytest.raises(ProspectiveCaptureError, match="derived version"):
        run_prospective_capture_review(payload)


def test_record_must_use_run_identity_and_conservative_observation_clock(payload):
    _records(payload)[0]["run_id"] = "00000000-0000-4000-8000-000000000002"
    with pytest.raises(ProspectiveCaptureError, match="run identity"):
        run_prospective_capture_review(payload)
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    _records(payload)[0]["version_observed_at"] = "2026-09-10T10:00:59Z"
    with pytest.raises(ProspectiveCaptureError, match="observation clock"):
        run_prospective_capture_review(payload)


@pytest.mark.parametrize("case", ["external", "multiple_roots", "fork", "first_seen"])
def test_complete_linear_revision_chain_is_required(payload, case):
    records = _records(payload)
    if case == "external":
        records[1]["supersedes_version_id"] = "f" * 64
    elif case == "multiple_roots":
        records[1]["supersedes_version_id"] = None
    elif case == "first_seen":
        records[1]["first_seen_at"] = "2026-09-10T10:00:00Z"
    else:
        records[2]["identity_method"] = "provider_id"
        records[2]["source_event_id"] = records[0]["source_event_id"]
        records[2]["version_id"] = expected_version_id(
            str(records[2]["source_event_id"]), str(records[2]["content_sha256"])
        )
        records[2]["supersedes_version_id"] = records[0]["version_id"]
    with pytest.raises(ProspectiveCaptureError, match="revision chain"):
        run_prospective_capture_review(payload)


@pytest.mark.parametrize("case", ["mapping", "before", "after", "duplicate", "ticker"])
def test_asset_link_provenance_fails_closed(payload, case):
    links = _records(payload)[1]["asset_links"]
    assert isinstance(links, list)
    first = links[0]
    assert isinstance(first, dict)
    if case == "mapping":
        first["mapping_version"] = "f" * 64
    elif case == "before":
        first["linked_at"] = "2026-09-10T10:00:59Z"
    elif case == "after":
        first["linked_at"] = "2026-09-10T10:05:01Z"
    elif case == "duplicate":
        second = links[1]
        assert isinstance(second, dict)
        second["ticker"] = first["ticker"]
    else:
        first["ticker"] = "BRK.B"
    with pytest.raises(ProspectiveCaptureError, match="asset_link|ticker"):
        run_prospective_capture_review(payload)


@pytest.mark.parametrize("case", ["sequence", "previous", "hash"])
def test_ledger_integrity_detects_mutation(payload, case):
    records = _records(payload)
    if case == "sequence":
        records[1]["sequence_no"] = 4
    elif case == "previous":
        records[1]["previous_record_sha256"] = "e" * 64
    else:
        records[2]["record_sha256"] = "e" * 64
    with pytest.raises(ProspectiveCaptureError, match="ledger"):
        run_prospective_capture_review(payload)


@pytest.mark.parametrize("level", ["bundle", "collector", "run", "record", "link"])
def test_extra_keys_are_rejected_at_every_boundary(payload, level):
    targets: dict[str, dict[str, object]] = {
        "bundle": payload,
        "collector": _collector(payload),
        "run": _run(payload),
        "record": _records(payload)[0],
        "link": _records(payload)[0]["asset_links"][0],  # type: ignore[index]
    }
    targets[level]["target_model"] = 0.5
    with pytest.raises(ProspectiveCaptureError, match="unexpected keys"):
        run_prospective_capture_review(payload)


def test_url_fallback_requires_exact_lowercase_digest(payload):
    _records(payload)[2]["source_event_id"] = "https://example.invalid/news/2"
    with pytest.raises(ProspectiveCaptureError, match="URL identity"):
        run_prospective_capture_review(payload)


def test_contract_hashes_are_bound_to_registered_bytes():
    assert hashlib.sha256((ROOT / PROTOCOL_PATH).read_bytes()).hexdigest() == PROTOCOL_SHA256
    assert hashlib.sha256((ROOT / BINDING_PATH).read_bytes()).hexdigest() == BINDING_SHA256


def test_tracked_synthetic_report_reproduces_exactly(payload):
    actual = serialize_capture_review(run_prospective_capture_review(payload))
    assert actual.encode() == REPORT.read_bytes()


@pytest.fixture
def cli():
    script = ROOT / "research/experiments/run_phase4_prospective_capture_review.py"
    return runpy.run_path(str(script))["main"]


def test_cli_creates_exact_report(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    assert cli(["--input", str(FIXTURE), "--output", str(output)]) == 0
    assert output.read_bytes() == REPORT.read_bytes()
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "succeeded"
    assert status["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"


def test_cli_invalid_input_is_redacted_and_creates_no_report(cli, tmp_path, capsys):
    bad = deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))
    secret = "mongodb+srv://user:password@example.invalid"
    bad["target_model"] = secret
    input_path = tmp_path / "bad.json"
    input_path.write_text(json.dumps(bad), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--input", str(input_path), "--output", str(output)]) == 1
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["error_code"] == "INVALID_SYNTHETIC_CAPTURE"
    assert secret not in stdout
    assert not output.exists()


def test_cli_rejects_nonfinite_json_without_output(cli, tmp_path, capsys):
    input_path = tmp_path / "bad.json"
    input_path.write_text('{"value": NaN}', encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--input", str(input_path), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "INVALID_JSON_INPUT"
    assert not output.exists()


def test_cli_requires_existing_output_parent(cli, tmp_path, capsys):
    output = tmp_path / "missing" / "review.json"
    assert cli(["--input", str(FIXTURE), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == (
        "OUTPUT_PARENT_MISSING"
    )
    assert not output.exists()


@pytest.mark.parametrize("kind", ["file", "symlink"])
def test_cli_refuses_existing_output(cli, tmp_path, capsys, kind):
    output = tmp_path / "review.json"
    if kind == "file":
        output.write_text("preserve", encoding="utf-8")
    else:
        target = tmp_path / "target.json"
        target.write_text("preserve", encoding="utf-8")
        output.symlink_to(target)
    assert cli(["--input", str(FIXTURE), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"
    assert output.read_text(encoding="utf-8") == "preserve"
