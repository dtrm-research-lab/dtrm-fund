"""Run the preregistered retrospective-salvage graph on synthetic data only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dtrm.phase4.retrospective_salvage import (
    GRAPH,
    SalvageError,
    serialize_salvage_report,
)
from dtrm.phase4.retrospective_salvage_io import SalvageIOError, run_synthetic_audit


def _reject_json_constant(value: str) -> None:
    del value
    raise ValueError("non-finite JSON number")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.is_symlink():
            raise SalvageIOError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise SalvageIOError("OUTPUT_PARENT_MISSING")
        payload = json.loads(
            args.synthetic_input.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
        report = run_synthetic_audit(payload)
        encoded = serialize_salvage_report(report)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded)
    except SalvageIOError as exc:
        error = str(exc)
    except (SalvageError, ValueError, TypeError, KeyError):
        error = "INVALID_SYNTHETIC_INPUT"
    except OSError:
        error = "FILE_IO_FAILED"
    else:
        print(
            json.dumps(
                {
                    "graph": GRAPH,
                    "status": "succeeded",
                    "execution_mode": "synthetic",
                    "scientific_assessment": report["scientific_assessment"],
                    "scientific_status": report["scientific_status"],
                    "total_documents": report["total_documents"],
                },
                sort_keys=True,
            )
        )
        return 0
    print(json.dumps({"graph": GRAPH, "status": "failed", "error_code": error}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
