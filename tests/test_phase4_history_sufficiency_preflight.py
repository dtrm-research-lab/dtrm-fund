"""Synthetic-only Phase IV contracts. No real source values or external credentials."""
from __future__ import annotations

import copy
import json

import pytest

from dtrm.phase4.history_sufficiency_preflight import (
    PreflightError,
    assess_synthetic_coverage,
    run_cli,
)


def sample() -> dict:
    return {
        "schema_version": "dtrm.phase4.history_sufficiency_fixture.v0",
        "dataset_role": "synthetic",
        "cohorts": [
            {"cohort_tag": "case_b", "candidate_count": 2, "bins": {"unknown_availability": 0, "zero": 1, "one_to_four": 0, "five_to_nineteen": 0, "twenty_plus": 1}},
            {"cohort_tag": "case_a", "candidate_count": 8, "bins": {"unknown_availability": 2, "zero": 1, "one_to_four": 2, "five_to_nineteen": 2, "twenty_plus": 1}},
        ],
    }


def test_valid_canonical_permutation_and_no_promotion() -> None:
    original = sample()
    first = assess_synthetic_coverage(original)
    original["cohorts"].reverse()
    second = assess_synthetic_coverage(original)
    assert first == second
    assert first["candidate_total"] == 10
    assert first["bins_total"] == {"unknown_availability": 2, "zero": 2, "one_to_four": 2, "five_to_nineteen": 2, "twenty_plus": 2}
    assert first["source_authenticated"] is False
    assert all(first[k] is False for k in ("history_construction_permitted", "training_permitted", "outcome_access_permitted", "scientific_counting_permitted"))
    assert first["scientific_status"] == "BLOCKED_SOURCE_AUDIT"


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(dataset_role="unaudited"),
    lambda x: x.update(schema_version="wrong"),
    lambda x: x.update(protected_outcome=1),
    lambda x: x["cohorts"].append(copy.deepcopy(x["cohorts"][0])),
    lambda x: x["cohorts"][0].update(cohort_tag="TSLA"),
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
