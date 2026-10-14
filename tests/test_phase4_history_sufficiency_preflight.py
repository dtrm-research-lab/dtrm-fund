"""Synthetic-only Phase IV contracts. No real source values or external credentials."""

from __future__ import annotations

import copy
import json
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.history_sufficiency_preflight import (
    PreflightError,
    SyntheticCoverageAssessment,
    assess_synthetic_coverage,
    run_cli,
)


def sample() -> dict:
    return {
        "schema_version": "dtrm.phase4.history_sufficiency_fixture.v0",
        "dataset_role": "synthetic",
        "cohorts": [
            {"cohort_tag": "case_02", "candidate_count": 2, "bins": {"unknown_availability": 0, "zero": 1, "one_to_four": 0, "five_to_nineteen": 0, "twenty_plus": 1}},
            {"cohort_tag": "case_01", "candidate_count": 8, "bins": {"unknown_availability": 2, "zero": 1, "one_to_four": 2, "five_to_nineteen": 2, "twenty_plus": 1}},
        ],
    }


def test_valid_canonical_permutation_and_no_promotion() -> None:
    original = sample()
    first = assess_synthetic_coverage(original)
    original["cohorts"].reverse()
    second = assess_synthetic_coverage(original)
    assert isinstance(first, SyntheticCoverageAssessment)
    assert first == second
    report = first.to_json()
    assert report["candidate_total"] == 10
    assert report["bins_total"] == {"unknown_availability": 2, "zero": 2, "one_to_four": 2, "five_to_nineteen": 2, "twenty_plus": 2}
    assert report["source_authenticated"] is False
    assert all(report[k] is False for k in ("history_construction_permitted", "training_permitted", "outcome_access_permitted", "scientific_counting_permitted"))
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"


def test_immutable_assessment_and_deep_serialization_copy() -> None:
    state = assess_synthetic_coverage(sample())
    with pytest.raises(FrozenInstanceError):
        state.candidate_total = 999
    with pytest.raises(FrozenInstanceError):
        state.cohorts[0].candidate_count = 999
    first_json = state.to_json()
    first_json["source_authenticated"] = True
    first_json["bins_total"]["zero"] = 999
    first_json["cohorts"][0]["bins"]["zero"] = 999
    second_json = state.to_json()
    assert second_json["source_authenticated"] is False
    assert second_json["bins_total"]["zero"] == 2
    assert second_json["cohorts"][0]["bins"]["zero"] == 1
    assert state.grand_counts == (2, 2, 2, 2, 2)


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(dataset_role="unaudited"),
    lambda x: x.update(schema_version="wrong"),
    lambda x: x.update(protected_outcome=1),
    lambda x: x["cohorts"].append(copy.deepcopy(x["cohorts"][0])),
    lambda x: x["cohorts"][0].update(cohort_tag="TSLA"),
    lambda x: x["cohorts"][0].update(cohort_tag="tsla"),
    lambda x: x["cohorts"][0].update(cohort_tag="case_a"),
    lambda x: x["cohorts"][0].update(cohort_tag="case_1"),
    lambda x: x["cohorts"][0].update(cohort_tag="case_00"),
    lambda x: x["cohorts"][0].update(cohort_tag="case_65"),
    lambda x: x["cohorts"][0].update(cohort_tag="2026-10-14"),
    lambda x: x["cohorts"][0].update(candidate_count=True),
    lambda x: x["cohorts"][0].update(candidate_count=0),
    lambda x: x["cohorts"][0].update(candidate_count=1_000_001),
    lambda x: x["cohorts"][0]["bins"].update(zero=-1),
    lambda x: x["cohorts"][0]["bins"].update(zero=1.0),
    lambda x: x["cohorts"][0]["bins"].update(zero=True),
    lambda x: x["cohorts"][0]["bins"].update(zero=2),
    lambda x: x["cohorts"][0]["bins"].update(target=4),
    lambda x: x["cohorts"].clear(),
    lambda x: x["cohorts"].extend(copy.deepcopy(x["cohorts"][0]) for _ in range(64)),
])
def test_fail_closed(mutation) -> None:
    data = sample()
    mutation(data)
    with pytest.raises(PreflightError, match="INVALID_SYNTHETIC_HISTORY_FIXTURE"):
        assess_synthetic_coverage(data)


def test_maximum_fixed_synthetic_tag_is_allowed() -> None:
    item = sample()["cohorts"][0]
    item["cohort_tag"] = "case_64"
    fixture = sample()
    fixture["cohorts"] = [item]
    report = assess_synthetic_coverage(fixture)
    assert report.cohorts[0].cohort_tag == "case_64"


def test_cli_exclusive_creation(tmp_path) -> None:
    input_path = tmp_path / "fixture.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(sample()), encoding="utf-8")
    assert run_cli(["--fixture", str(input_path), "--output", str(output_path)]) == 0
    old = output_path.read_bytes()
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(input_path), "--output", str(output_path)])
    assert output_path.read_bytes() == old


def test_cli_reject_symlink(tmp_path) -> None:
    input_path = tmp_path / "fixture.json"
    target_path = tmp_path / "untouched"
    output_path = tmp_path / "out"
    input_path.write_text(json.dumps(sample()), encoding="utf-8")
    target_path.write_text("safe", encoding="utf-8")
    output_path.symlink_to(target_path)
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(input_path), "--output", str(output_path)])
    assert target_path.read_text(encoding="utf-8") == "safe"


def test_invalid_fixture_does_not_create_report(tmp_path) -> None:
    input_path = tmp_path / "fixture.json"
    output_path = tmp_path / "out"
    bad = sample()
    bad["dataset_role"] = "real"
    input_path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(input_path), "--output", str(output_path)])
    assert not output_path.exists()


@pytest.mark.parametrize("original,replacement", [
    ('"dataset_role": "synthetic"', '"dataset_role": "real", "dataset_role": "synthetic"'),
    ('"cohorts": [', '"cohorts": [], "cohorts": ['),
    ('"zero": 1', '"zero": 2, "zero": 1'),
    ('"candidate_count": 2', '"candidate_count": 999, "candidate_count": 2'),
])
def test_cli_rejects_duplicate_json_keys(tmp_path, original, replacement) -> None:
    fixture_path = tmp_path / "fixture.json"
    output_path = tmp_path / "output.json"
    encoded = json.dumps(sample())
    assert original in encoded
    fixture_path.write_text(encoded.replace(original, replacement, 1), encoding="utf-8")
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(fixture_path), "--output", str(output_path)])
    assert not output_path.exists()


def test_cli_fsync_failure_leaves_no_report_or_temp(tmp_path, monkeypatch) -> None:
    fixture_path = tmp_path / "fixture.json"
    output_path = tmp_path / "output.json"
    fixture_path.write_text(json.dumps(sample()), encoding="utf-8")

    def fail_durability(_fd):
        raise OSError("simulated private durability failure")

    monkeypatch.setattr("dtrm.phase4.history_sufficiency_preflight.os.fsync", fail_durability)
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(fixture_path), "--output", str(output_path)])
    assert not output_path.exists()
    assert list(tmp_path.glob(".phase4-history-*")) == []


def test_cli_link_failure_leaves_no_report_or_temp(tmp_path, monkeypatch) -> None:
    fixture_path = tmp_path / "fixture.json"
    output_path = tmp_path / "output.json"
    fixture_path.write_text(json.dumps(sample()), encoding="utf-8")

    def fail_publish(_source, _dest):
        raise OSError("simulated private publish failure")

    monkeypatch.setattr("dtrm.phase4.history_sufficiency_preflight.os.link", fail_publish)
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(fixture_path), "--output", str(output_path)])
    assert not output_path.exists()
    assert list(tmp_path.glob(".phase4-history-*")) == []


def test_cli_external_destination_race_never_overwrites(tmp_path, monkeypatch) -> None:
    from pathlib import Path

    fixture_path = tmp_path / "fixture.json"
    output_path = tmp_path / "output.json"
    fixture_path.write_text(json.dumps(sample()), encoding="utf-8")

    def racing_writer(_source, target):
        Path(target).write_text("other writer", encoding="utf-8")
        raise FileExistsError("simulated concurrent destination")

    monkeypatch.setattr("dtrm.phase4.history_sufficiency_preflight.os.link", racing_writer)
    with pytest.raises(SystemExit):
        run_cli(["--fixture", str(fixture_path), "--output", str(output_path)])
    assert output_path.read_text(encoding="utf-8") == "other writer"
    assert list(tmp_path.glob(".phase4-history-*")) == []
