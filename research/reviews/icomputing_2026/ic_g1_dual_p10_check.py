#!/usr/bin/env python3
"""Read-only strict dual P10 numeric confirmation from G1.2b aggregate JSON."""
import argparse
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prior",required=True)
    args=p.parse_args()
    data=json.loads(Path(args.prior).expanduser().read_text(encoding="utf-8"))
    if data.get("schema_version")!="dtrm.ic.g1.rowlevel_parity.v1":
        raise ValueError("Wrong G1.2b schema")
    if data.get("status")!="HISTORICAL_NUMERIC_PARITY_PASS_PROVENANCE_PENDING":
        raise ValueError("G1.2b was not PASS")
    base=data["baseline_numeric_parity"]
    masks=data["p10_veto_parity"]
    columns=data["p10_numeric_parity_candidates"]
    checks={
        "baseline_40320": base.get("within_tolerance") is True and base.get("rows")==40320 and base.get("exceeding_tolerance")==0,
        "p10_raw_40320": columns.get("p10_raw",{}).get("within_tolerance") is True and columns.get("p10_raw",{}).get("rows")==40320 and columns.get("p10_raw",{}).get("exceeding_tolerance")==0,
        "p10_calibrated_40320": columns.get("p10_calibrated",{}).get("within_tolerance") is True and columns.get("p10_calibrated",{}).get("rows")==40320 and columns.get("p10_calibrated",{}).get("exceeding_tolerance")==0,
        "v1_veto": masks.get("v1_absolute_p10_veto",{}).get("exact_pass_match") is True and masks.get("v1_absolute_p10_veto",{}).get("disagreements")==0,
        "v4_veto": masks.get("exact_pass_match") is True and masks.get("disagreements")==0 and masks.get("reconstructed_pass")==23348,
    }
    for name,passed in checks.items():
        print(name,"PASS" if passed else "FAIL")
    for col in ("p10_raw","p10_calibrated"):
        ref=columns.get(col,{})
        print(col,"max_abs_difference=",ref.get("max_abs_difference"))
    print("G1.2c:", "DUAL_P10_NUMERIC_PARITY_PASS_PROVENANCE_OPEN" if all(checks.values()) else "DUAL_P10_NUMERIC_PARITY_FAIL")
    print("Input: aggregate JSON only; no pickle, model or prospective cohort opened.")
    return 0 if all(checks.values()) else 2

if __name__=="__main__":
    raise SystemExit(main())
