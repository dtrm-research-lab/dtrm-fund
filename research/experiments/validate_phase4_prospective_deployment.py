"""Validate the Phase-IV prospective deployment manifest without external I/O."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dtrm.phase4.prospective_deployment import (
    GRAPH,
    ProspectiveDeploymentError,
    canonical_manifest_bytes,
    normalize_deployment_manifest,
    run_deployment_review,
    serialize_deployment_review,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT
    / "research/contracts/DTRM_PHASE4_PROSPECTIVE_DEPLOYMENT_MANIFEST_V0.json"
)


def _reject_constant(value: str) -> None:
    del value
    raise ValueError("non-finite JSON number")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.is_symlink():
            raise OSError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise OSError("OUTPUT_PARENT_MISSING")
        manifest_bytes = args.manifest.read_bytes()
        payload = json.loads(
            manifest_bytes.decode("utf-8"), parse_constant=_reject_constant
        )
        manifest = normalize_deployment_manifest(payload)
        if manifest_bytes != canonical_manifest_bytes(manifest):
            raise ProspectiveDeploymentError("manifest is not canonically serialized")
        review = run_deployment_review(payload)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(serialize_deployment_review(review))
    except ProspectiveDeploymentError:
        error = "INVALID_DEPLOYMENT_MANIFEST"
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
        print(
            json.dumps(
                {
                    "engineering_status": review.to_dict()["engineering_status"],
                    "graph": GRAPH,
                    "scientific_status": review.to_dict()["scientific_status"],
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
