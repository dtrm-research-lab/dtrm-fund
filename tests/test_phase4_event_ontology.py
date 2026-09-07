"""Synthetic acceptance and failure cases from the preregistered ontology."""

import hashlib
import json
import runpy
import subprocess
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.events import normalize_observations
from dtrm.phase4.ontology_graph import GraphFailure, run_ontology_review

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase4_event_batch_v0.json"


@pytest.fixture
def batch():
    return json.loads(FIXTURE.read_text())


def test_valid_synthetic_batch_reports_counts_and_remains_scientifically_blocked(batch):
    result = run_ontology_review(batch).to_dict()
    assert result["completed_nodes"] == [
        "normalize_observations", "validate_revision_chains", "assess_metadata_completeness",
    ]
    assert (result["version_count"], result["logical_event_count"], result["asset_link_count"]) == (3, 2, 4)
    assert result["unknown_availability_count"] == 1
    assert result["engineering_status"] == "PASS_ONTOLOGY_SCHEMA"
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert result["training_permitted"] is False
    assert result["outcome_access_permitted"] is False


def test_revision_and_late_asset_link_are_never_backdated_to_first_seen(batch):
    links = run_ontology_review(batch).links
    assert [link.available_at for link in links] == [
        "2026-07-07T10:02:00Z", "2026-07-07T10:05:00Z", "2026-07-08T09:00:00Z", None,
    ]


def test_day_precision_and_unknowns_survive_normalization(batch):
    record = normalize_observations(batch).events[-1]
    assert record.published_at == "2026-07-07"
    assert record.publication_precision == "day"
    assert record.version_observed_at is None
    assert record.availability(record.asset_links[0]) is None


def test_unknown_publication_does_not_prevent_recording_known_observation(batch):
    record = batch["events"][0]
    record["published_at"] = None
    record["publication_precision"] = "unknown"
    assert run_ontology_review(batch).links[0].available_at == "2026-07-07T10:02:00Z"


def test_timezone_equivalent_and_reordered_batches_have_identical_reviews(batch):
    expected = run_ontology_review(batch).to_dict()
    batch["events"][0]["version_observed_at"] = "2026-07-07T12:01:00+02:00"
    batch["events"].reverse()
    for event in batch["events"]:
        event["asset_links"].reverse()
    assert run_ontology_review(batch).to_dict() == expected


def test_normalized_state_is_immutable_and_detached_from_input(batch):
    normalized = normalize_observations(batch)
    with pytest.raises(FrozenInstanceError):
        normalized.events[0].version_id = "changed"
    batch["events"][0]["asset_links"][0]["ticker"] = "ZZZ"
    assert normalized.events[0].asset_links[0].ticker == "AAA"


@pytest.mark.parametrize("level", ["batch", "event", "link"])
def test_outcome_fields_are_rejected_at_every_boundary(batch, level):
    targets = {"batch": batch, "event": batch["events"][0],
               "link": batch["events"][0]["asset_links"][0]}
    targets[level]["target_model"] = 0.9
    with pytest.raises(GraphFailure) as error:
        run_ontology_review(batch)
    assert error.value.node == "normalize_observations"


@pytest.mark.parametrize("field", ["occurred_at", "first_seen_at", "version_observed_at"])
def test_naive_event_instants_are_rejected(batch, field):
    batch["events"][0][field] = "2026-07-07T10:01:00"
    with pytest.raises(GraphFailure):
        run_ontology_review(batch)


@pytest.mark.parametrize("value", ["2026-07-07", "2026-07-07T10:02:00", "bad"])
def test_link_availability_requires_a_timezone_aware_instant(batch, value):
    batch["events"][0]["asset_links"][0]["linked_at"] = value
    with pytest.raises(GraphFailure):
        run_ontology_review(batch)


@pytest.mark.parametrize("precision,value", [
    ("instant", "2026-07-07"), ("day", "2026-02-30"), ("day", "20260707"),
    ("unknown", "2026-07-07"), ("instant", None), ("minute", None),
])
def test_publication_precision_cannot_be_invented(batch, precision, value):
    batch["events"][0]["publication_precision"] = precision
    batch["events"][0]["published_at"] = value
    with pytest.raises(GraphFailure):
        run_ontology_review(batch)


@pytest.mark.parametrize("field,value", [
    ("content_sha256", "short"), ("content_sha256", "A" * 64),
    ("source", "new_vendor"), ("source_event_id", " "), ("version_id", None),
])
def test_invalid_identity_and_content_binding_are_rejected(batch, field, value):
    batch["events"][0][field] = value
    with pytest.raises(GraphFailure):
        run_ontology_review(batch)


def test_duplicate_links_and_aliases_are_not_silently_normalized(batch):
    event = batch["events"][0]
    event["asset_links"][1]["ticker"] = "AAA"
    with pytest.raises(GraphFailure, match="duplicate ticker"):
        run_ontology_review(batch)
    event["asset_links"][1]["ticker"] = "BRK.B"
    with pytest.raises(GraphFailure, match="canonical"):
        run_ontology_review(batch)


def test_duplicate_version_identity_is_rejected(batch):
    batch["events"].append(deepcopy(batch["events"][0]))
    with pytest.raises(GraphFailure, match="duplicate version"):
        run_ontology_review(batch)


@pytest.mark.parametrize("case", ["missing", "cycle", "multiple_roots", "fork", "backwards", "first_seen"])
def test_revision_lineage_failures_stop_the_graph(batch, case):
    first, revision = batch["events"][:2]
    if case == "missing":
        revision["supersedes_version_id"] = "absent"
    elif case == "cycle":
        first["supersedes_version_id"] = "v2"
    elif case == "multiple_roots":
        revision["supersedes_version_id"] = None
    elif case == "fork":
        third = deepcopy(revision)
        third["version_id"] = "v3"
        batch["events"].append(third)
    elif case == "backwards":
        first["version_observed_at"] = "2026-07-09T09:00:00Z"
    elif case == "first_seen":
        revision["first_seen_at"] = "2026-07-07T10:00:00Z"
    with pytest.raises(GraphFailure) as error:
        run_ontology_review(batch)
    assert error.value.node == "validate_revision_chains"


def test_version_before_logical_first_observation_is_rejected(batch):
    batch["events"][0]["version_observed_at"] = "2026-07-07T09:59:00Z"
    with pytest.raises(GraphFailure, match="precedes logical"):
        run_ontology_review(batch)


@pytest.mark.parametrize("reverse_input", [False, True])
@pytest.mark.parametrize("logical_seen,valid", [
    ("2026-07-07T10:00:00Z", True), ("2026-07-07T10:02:00Z", False),
])
def test_logical_first_seen_constrains_versions_that_omit_it(
        batch, reverse_input, logical_seen, valid):
    first, revision = batch["events"][:2]
    first["first_seen_at"] = None
    revision["first_seen_at"] = logical_seen
    if reverse_input:
        batch["events"].reverse()
    if not valid:
        with pytest.raises(GraphFailure, match="precedes logical") as error:
            run_ontology_review(batch)
        assert error.value.node == "validate_revision_chains"
    else:
        result = run_ontology_review(batch).to_dict()
        assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
        assert normalize_observations(batch).events[0].first_seen_at is None


@pytest.mark.parametrize("tip_observed,valid", [
    ("2026-07-07T10:00:00Z", False), ("2026-07-07T10:01:00Z", True),
    ("2026-07-08T09:00:00Z", True), (None, True),
])
def test_unknown_revision_cannot_hide_backwards_known_times(batch, tip_observed, valid):
    first, middle = batch["events"][:2]
    first["first_seen_at"] = middle["first_seen_at"] = None
    middle["version_observed_at"] = None
    tip = deepcopy(middle)
    # Scientific chronology must follow predecessor links, not lexical IDs or input order.
    tip["version_id"] = "a-tip"
    tip["supersedes_version_id"] = middle["version_id"]
    tip["version_observed_at"] = tip_observed
    batch["events"].insert(0, tip)
    if not valid:
        with pytest.raises(GraphFailure, match="move backwards") as error:
            run_ontology_review(batch)
        assert error.value.node == "validate_revision_chains"
    else:
        result = run_ontology_review(batch).to_dict()
        assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
        assert middle["version_observed_at"] is None


def test_missing_link_timestamp_remains_unknown_even_with_known_version(batch):
    batch["events"][0]["asset_links"][0]["linked_at"] = None
    assert run_ontology_review(batch).links[0].available_at is None


def test_unlinked_news_is_preserved(batch):
    batch["events"][2]["asset_links"] = []
    result = run_ontology_review(batch).to_dict()
    assert (result["version_count"], result["asset_link_count"]) == (3, 3)


@pytest.mark.parametrize("field,value", [
    ("schema_version", "unknown"), ("dataset_role", "confirmed"), ("events", []),
])
def test_batch_contract_cannot_promote_or_accept_empty_evidence(batch, field, value):
    batch[field] = value
    with pytest.raises(GraphFailure):
        run_ontology_review(batch)


def test_complete_unaudited_metadata_still_cannot_authorize_training(batch):
    batch["dataset_role"] = "unaudited"
    batch["events"] = batch["events"][:2]
    result = run_ontology_review(batch).to_dict()
    assert result["unknown_availability_count"] == 0
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert result["training_permitted"] is False


def test_cli_creates_review_and_refuses_to_overwrite(tmp_path):
    output = tmp_path / "review.json"
    command = [sys.executable, str(ROOT / "research/experiments/run_phase4_ontology_review.py"),
               "--input", str(FIXTURE), "--output", str(output)]
    first = subprocess.run(command, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    original = output.read_bytes()
    second = subprocess.run(command, capture_output=True, text=True)
    assert second.returncode == 1
    assert output.read_bytes() == original


def test_cli_failure_does_not_write_a_success_artifact(batch, tmp_path):
    batch["events"][0]["target_model"] = 1
    source = tmp_path / "bad.json"
    source.write_text(json.dumps(batch))
    output = tmp_path / "review.json"
    result = subprocess.run([
        sys.executable, str(ROOT / "research/experiments/run_phase4_ontology_review.py"),
        "--input", str(source), "--output", str(output),
    ], capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)["node"] == "normalize_observations"
    assert not output.exists()


def test_preservation_gate_rejects_changed_mm1_bytes_in_disposable_copy(tmp_path, monkeypatch):
    namespace = runpy.run_path(str(ROOT / "research/experiments/validate_phase4_source_preservation.py"))
    # Exercise real Git objects in a disposable miniature repository. This unit
    # test also works in the inherited workflow's shallow/editable checkout.
    # The Phase-IV CI gate separately checks all 157 real inherited files.
    altered = tmp_path / "src/dtrm/phase3_mm1_optimizer.py"
    altered.parent.mkdir(parents=True)
    altered.write_text("# synthetic frozen policy\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qm", "synthetic frozen source"], cwd=tmp_path, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=tmp_path, text=True).strip()
    contract = tmp_path / "research/contracts/DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md"
    contract.parent.mkdir(parents=True)
    contract.write_text("# synthetic contract\n")
    digest = hashlib.sha256(contract.read_bytes()).hexdigest()
    binding = contract.parent / "DTRM_PHASE4_SOURCE_BINDING_V0.json"
    binding.write_text(json.dumps({"inherited_commit": base, "inherited_tree": tree,
                                   "stage0_contract_sha256": digest}))
    checker = namespace["check_preservation"]
    for key, value in {"BASE_COMMIT": base, "BASE_TREE": tree, "CONTRACT_SHA256": digest}.items():
        monkeypatch.setitem(checker.__globals__, key, value)
    assert checker(tmp_path)["status"] == "PASS_SOURCE_PRESERVATION"
    altered.write_bytes(altered.read_bytes() + b"\n# unauthorized policy change\n")
    with pytest.raises(ValueError, match="inherited files changed"):
        checker(tmp_path)
