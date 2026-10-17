"""Closed synthetic source-proof cases; no private article/ticker/source data."""
from __future__ import annotations

import json
import runpy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.temporal_proof_obligations import (
    ERROR,
    AvailabilityClaims,
    ProofObligationError,
    SyntheticWitness,
    assess_synthetic_witness,
    build_synthetic_report,
)

CUT = "2026-10-15T00:00:00Z"
BEFORE = "2026-10-14T20:00:00Z"
AT = CUT
AFTER = "2026-10-15T00:00:01Z"
PUB = "2026-10-12T00:00:00Z"


def claims(
    *,
    source: str | None = None,
    link: str | None = None,
    derived: str | None = None,
    price: str | None = None,
    receipts: bool = False,
) -> AvailabilityClaims:
    return AvailabilityClaims(
        source, link, derived, price, receipts, receipts, receipts, receipts
    )


def sample(
    tag: str = "case_one",
    archived: str | None = BEFORE,
    proof: AvailabilityClaims | None = None,
    family: str = "family_fake_a",
) -> SyntheticWitness:
    return SyntheticWitness(tag, family, CUT, PUB, archived, proof or claims())


def test_publication_early_archive_late_does_not_backdate_links() -> None:
    report = assess_synthetic_witness(sample(archived=AFTER))
    assert report.archived_witness == "NO_PRE_CUTOFF_ARCHIVE"
    assert report.proof_shape == "INCOMPLETE_PROOF"
    assert report.historical_absence == "UNKNOWN"
    assert report.real_source_admission_permitted is False


def test_archive_prior_positive_never_authenticates_original_first_seen() -> None:
    report = assess_synthetic_witness(sample())
    assert report.archived_witness == "PRIOR_ARCHIVED_POSITIVE"
    assert report.proof_shape == "INCOMPLETE_PROOF"
    assert report.original_first_seen_authenticated is False


def test_complete_synthetic_receipt_shape_cannot_promote_real_source() -> None:
    status = assess_synthetic_witness(sample(
        proof=claims(
            source=BEFORE, link=BEFORE, derived=BEFORE, price=BEFORE,
            receipts=True,
        ),
    ))
    assert status.proof_shape == "SYNTHETIC_PROOF_SHAPE_COMPLETE"
    assert status.archived_witness == "PRIOR_ARCHIVED_POSITIVE"
    assert status.real_source_admission_permitted is False
    assert status.original_first_seen_authenticated is False


@pytest.mark.parametrize("missing", ["source", "link", "derived", "price"])
def test_missing_exact_dependency_blocks_even_if_publication_and_archive_prior(
    missing: str,
) -> None:
    vals: dict[str, str | None] = dict(
        source=BEFORE, link=BEFORE, derived=BEFORE, price=BEFORE
    )
    vals[missing] = None
    c = AvailabilityClaims(
        vals["source"], vals["link"], vals["derived"], vals["price"],
        vals["source"] is not None, vals["link"] is not None,
        vals["derived"] is not None, vals["price"] is not None,
    )
    status = assess_synthetic_witness(sample(proof=c))
    assert status.proof_shape == "INCOMPLETE_PROOF"


@pytest.mark.parametrize("role", ["source", "link", "derived", "price"])
@pytest.mark.parametrize("bad_time", [AT, AFTER])
def test_future_or_equal_claim_fails_strict_cutoff(
    role: str, bad_time: str,
) -> None:
    vals = dict(source=BEFORE, link=BEFORE, derived=BEFORE, price=BEFORE)
    vals[role] = bad_time
    status = assess_synthetic_witness(sample(proof=claims(**vals, receipts=True)))
    assert status.proof_shape == "FUTURE_CLAIM"
    assert status.archived_witness == "PRIOR_ARCHIVED_POSITIVE"
    assert status.real_source_admission_permitted is False


def test_future_claim_precedes_missing_proof_status() -> None:
    status = assess_synthetic_witness(sample(
        proof=AvailabilityClaims(BEFORE, AFTER, None, None, True, True, False, False),
    ))
    assert status.proof_shape == "FUTURE_CLAIM"


def test_equal_archive_clock_not_a_prior_witness() -> None:
    status = assess_synthetic_witness(sample(archived=AT))
    assert status.archived_witness == "NO_PRE_CUTOFF_ARCHIVE"


def test_source_without_prior_archive_still_noncounting() -> None:
    status = assess_synthetic_witness(sample(
        archived=None,
        proof=claims(
            source=BEFORE, link=BEFORE, derived=BEFORE, price=BEFORE,
            receipts=True,
        ),
    ))
    assert status.archived_witness == "NO_PRE_CUTOFF_ARCHIVE"
    assert status.proof_shape == "SYNTHETIC_PROOF_SHAPE_COMPLETE"
    assert status.real_source_admission_permitted is False


@pytest.mark.parametrize("bad", [
    "2026-10-14", "2026-10-14T20:00:00", "2026-10-14T20:00:00+02:00",
    "2026-10-14T20:00:00.001Z", "2026-02-30T20:00:00Z",
    "2026-10-14T25:00:00Z", "2026-10-14T20:00:00z",
])
def test_malformed_or_naive_time_rejected_with_fixed_error(bad: str) -> None:
    with pytest.raises(ProofObligationError, match=ERROR):
        assess_synthetic_witness(sample(archived=bad))
    with pytest.raises(ProofObligationError, match=ERROR):
        assess_synthetic_witness(sample(proof=AvailabilityClaims(
            bad, None, None, None,
        )))


def test_receipt_without_arrival_clock_is_inconsistent_and_rejected() -> None:
    with pytest.raises(ProofObligationError, match=ERROR):
        assess_synthetic_witness(sample(proof=AvailabilityClaims(
            None, BEFORE, BEFORE, BEFORE, True, True, True, True,
        )))


def test_nonbool_receipt_is_rejected() -> None:
    with pytest.raises(ProofObligationError, match=ERROR):
        assess_synthetic_witness(sample(proof=AvailabilityClaims(
            BEFORE, BEFORE, BEFORE, BEFORE, 1, True, True, True,  # type: ignore[arg-type]
        )))


@pytest.mark.parametrize("tag", ["private@email.com", "MSFT", "", "case_ABC", "case_foo/bar", "x" * 80])
def test_unsafe_or_raw_identifier_rejected(tag: str) -> None:
    with pytest.raises(ProofObligationError, match=ERROR):
        assess_synthetic_witness(sample(tag=tag))


def test_immutable_objects() -> None:
    with pytest.raises(FrozenInstanceError):
        sample().decision_at = AFTER  # type: ignore[misc]


def test_deterministic_aggregates_and_scientific_firewall() -> None:
    a = sample("case_alpha")
    b = sample("case_beta", archived=AFTER)
    c = sample("case_gamma", proof=claims(
        source=BEFORE, link=BEFORE, derived=BEFORE, price=BEFORE,
        receipts=True,
    ))
    report = build_synthetic_report([c, a, b])
    assert report == build_synthetic_report([b, c, a])
    assert report["sample_count"] == 3
    assert report["prior_archived_positive_count"] == 2
    assert report["synthetic_shape_complete_count"] == 1
    assert report["unknown_historical_absence_count"] == 3
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for key in (
        "source_metadata_independently_authenticated",
        "historical_first_seen_authenticated",
        "negative_history_authenticated",
        "source_completeness_authenticated",
        "price_clock_authenticated",
        "rights_authenticated",
        "real_source_admission_permitted",
        "history_construction_permitted",
        "model_fitting_permitted",
        "outcomes_access_permitted",
        "mm1_execution_permitted",
        "scientific_counting_permitted",
    ):
        assert report[key] is False
    assert [item["case_tag"] for item in report["cases"]] == [
        "case_alpha", "case_beta", "case_gamma"
    ]


def test_duplicate_case_tags_and_bounds_fail_closed() -> None:
    with pytest.raises(ProofObligationError, match=ERROR):
        build_synthetic_report([sample(), sample()])
    with pytest.raises(ProofObligationError, match=ERROR):
        build_synthetic_report([])
    with pytest.raises(ProofObligationError, match=ERROR):
        build_synthetic_report([sample(f"case_{i}") for i in range(65)])


def test_closed_fictional_cli_does_not_serialize_source_or_promote(
    capsys: pytest.CaptureFixture[str],
) -> None:
    entry = Path(__file__).resolve().parents[1] / "research" / "experiments" / "run_phase4_temporal_proof_obligations.py"
    main = runpy.run_path(str(entry), run_name="synthetic_only_test")["main"]
    assert main() == 0
    raw = capsys.readouterr().out
    result = json.loads(raw)
    expected = (Path(__file__).resolve().parents[1] / "research" / "reports" / "DTRM_PHASE4_TEMPORAL_PROOF_OBLIGATIONS_SYNTHETIC_V0.json").read_text()
    assert raw == expected
    assert result["sample_count"] == 5
    assert result["prior_archived_positive_count"] == 3
    assert result["synthetic_shape_complete_count"] == 1
    assert result["future_claim_count"] == 1
    assert result["unknown_historical_absence_count"] == 5
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert result["real_source_admission_permitted"] is False
    assert result["model_fitting_permitted"] is False
    assert result["outcomes_access_permitted"] is False
    assert "article" not in raw.lower()
    assert "ticker" not in raw.lower()
    assert "url" not in raw.lower()
