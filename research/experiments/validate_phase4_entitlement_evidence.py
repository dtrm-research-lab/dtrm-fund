"""Validate the Phase-IV entitlement evidence intake without external I/O."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from dtrm.phase4.entitlement_evidence_intake import (
    GRAPH,
    EntitlementEvidenceError,
    canonical_statement_bytes,
    normalize_entitlement_evidence,
    review_entitlement_evidence,
    serialize_review,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATEMENT = (
    ROOT / "research/contracts/DTRM_PHASE4_ENTITLEMENT_EVIDENCE_STATEMENT_V0.json"
)


def _reject_constant(value: str) -> None:
    del value
    raise ValueError("non-finite JSON number")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statement", type=Path, default=DEFAULT_STATEMENT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.is_symlink():
            raise OSError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise OSError("OUTPUT_PARENT_MISSING")
        statement_bytes = args.statement.read_bytes()
        payload = json.loads(
            statement_bytes.decode("utf-8"), parse_constant=_reject_constant
        )
        normalized = normalize_entitlement_evidence(payload)
        if statement_bytes != canonical_statement_bytes(normalized):
            raise EntitlementEvidenceError("statement is not canonically serialized")
        review = review_entitlement_evidence(payload)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(serialize_review(review))
    except EntitlementEvidenceError:
        error = "INVALID_ENTITLEMENT_EVIDENCE_STATEMENT"
    except (ValueError, TypeError, KeyError, UnicodeError):
        error = "INVALID_JSON_INPUT"
    except OSError as exc:
        code = str(exc)
        error = (
            code
            if code in {"OUTPUT_EXISTS", "OUTPUT_PARENT_MISSING"}
            else "FILE_IO_FAILED"
        )
    else:
        report = review.to_dict()
        permissions = cast(dict[str, object], report["permissions"])
        print(
            json.dumps(
                {
                    "engineering_status": report["engineering_status"],
                    "evidence_state": report["evidence_state"],
                    "graph": GRAPH,
                    "scientific_status": permissions["scientific_status"],
                    "status": "succeeded",
                },
                sort_keys=True,
            )
        )
        return 0
    print(
        json.dumps(
            {"error_code": error, "graph": GRAPH, "status": "failed"},
            sort_keys=True,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
