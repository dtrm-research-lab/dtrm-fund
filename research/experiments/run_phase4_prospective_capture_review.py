"""Validate one synthetic prospective-capture bundle; no production I/O."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dtrm.phase4.prospective_capture import (
    GRAPH,
    ProspectiveCaptureError,
    run_prospective_capture_review,
    serialize_capture_review,
)


def _reject_constant(value: str) -> None:
    del value
    raise ValueError("non-finite JSON number")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.is_symlink():
            raise OSError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise OSError("OUTPUT_PARENT_MISSING")
        payload = json.loads(
            args.input.read_text(encoding="utf-8"), parse_constant=_reject_constant
        )
        review = run_prospective_capture_review(payload)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(serialize_capture_review(review))
    except ProspectiveCaptureError:
        error = "INVALID_SYNTHETIC_CAPTURE"
    except (ValueError, TypeError, KeyError):
        error = "INVALID_JSON_INPUT"
    except OSError as exc:
        code = str(exc)
        error = code if code in {"OUTPUT_EXISTS", "OUTPUT_PARENT_MISSING"} else "FILE_IO_FAILED"
    else:
        print(
            json.dumps(
                {
                    "graph": GRAPH,
                    "status": "succeeded",
                    "scientific_status": review.to_dict()["scientific_status"],
                },
                sort_keys=True,
            )
        )
        return 0
    print(json.dumps({"error_code": error, "graph": GRAPH, "status": "failed"}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
