"""Read one event batch and create one new review; no model or provider access."""

import argparse
import json
from pathlib import Path

from dtrm.phase4.ontology_graph import GRAPH_ID, GraphFailure, run_ontology_review


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_ontology_review(payload).to_dict()
        serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
    except (GraphFailure, ValueError, OSError) as exc:
        print(json.dumps({"graph": GRAPH_ID, "status": "failed",
                          "node": exc.node if isinstance(exc, GraphFailure) else "file_boundary",
                          "error": str(exc)}))
        return 1
    print(json.dumps({"graph": GRAPH_ID, "status": "succeeded",
                      "scientific_status": result["scientific_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
