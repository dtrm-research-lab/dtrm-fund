from __future__ import annotations

import argparse
from pathlib import Path

from dtrm.phase4.prospective_campaign_v2_closure import validate_files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(
            "research/evidence/phase4_prospective_campaign_v2_decisive_failure_v1.json"
        ),
    )
    parser.add_argument(
        "--statement",
        type=Path,
        default=Path(
            "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAMPAIGN_V2_CLOSURE_STATEMENT_V1.json"
        ),
    )
    args = parser.parse_args()
    validate_files(args.evidence, args.statement)
    print("PASS_PHASE4_PROSPECTIVE_CAMPAIGN_V2_DECISIVE_CLOSURE_V1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
