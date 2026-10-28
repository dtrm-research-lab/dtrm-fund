"""Reproducible G4.9c offline learned-policy engineering benchmark.

No LLM; no human observations; no statistical noninferiority. Reports every
synthetic evaluation case in aggregate, without exporting its hidden labels.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path

from g49c_agent import POLICY_ORDER, PROTOCOL_COMMIT, fit, select_candidate
from g49c_world import (EVAL_N, SEED, TRAIN_N, SCHEMA, canonical_sha,
                         make_worlds, oracle_utility, public_case_commitments,
                         training_rows)


def benchmark() -> dict:
    train, heldout = make_worlds()
    agent = fit(training_rows(train))  # no heldout labels passed to fit!
    learned_policies = [agent.choose(w.public) for w in heldout]
    if len(learned_policies) != EVAL_N:
        raise AssertionError("Lost heldout evaluations")

    choice_counts: Counter[str] = Counter()
    utilities = {"LEARNED_DELEGATED":[], "FIXED_BALANCED":[],
                 "HINDSIGHT_ORACLE_CEILING":[]}
    abstentions = {"LEARNED_DELEGATED":0, "FIXED_BALANCED":0,
                   "HINDSIGHT_ORACLE_CEILING":0}
    delta=[]
    invalid=0
    oracle_upper_exceeded=0
    for world, policy in zip(heldout, learned_policies):
        chosen = {"LEARNED_DELEGATED":policy,
                  "FIXED_BALANCED":"balanced",
                  "HINDSIGHT_ORACLE_CEILING":max(
                      POLICY_ORDER, key=lambda p: oracle_utility(world,p))}
        choice_counts[policy]+=1
        for arm, p in chosen.items():
            candidate = select_candidate(world.public,p)
            utility = oracle_utility(world,p)
            if candidate is None:
                abstentions[arm]+=1
            else:
                if not candidate["verified"] or candidate["blocked"] or candidate["risk"]>5:
                    invalid+=1
            utilities[arm].append(float(utility))
        delta.append(utilities["LEARNED_DELEGATED"][-1]
                     - utilities["FIXED_BALANCED"][-1])
        if (utilities["LEARNED_DELEGATED"][-1]
            > utilities["HINDSIGHT_ORACLE_CEILING"][-1]+1e-9):
            oracle_upper_exceeded+=1
    if invalid or oracle_upper_exceeded:
        raise AssertionError("Invalid hard guard or evaluated oracle ceiling")
    if len(choice_counts)<2:
        raise AssertionError("Vacuous learned policy always chose one policy")
    report={
        "schema_version":SCHEMA,
        "protocol_commit":PROTOCOL_COMMIT,
        "status":"SYNTHETIC_LEARNED_POLICY_HOLDOUT_ENGINEERING_ONLY",
        "participant_count":0,
        "actual_llm_agent_count":0,
        "actual_human_authority_observations":0,
        "noninferiority":"NOT_TESTED",
        "seed":SEED,
        "training_cases":TRAIN_N,
        "heldout_cases":EVAL_N,
        "train":public_case_commitments(train),
        "heldout":public_case_commitments(heldout),
        "agent":{"model":"regularized_linear_policy_value_estimator",
                 "training_policy_rows":agent.train_policy_rows,
                 "coefficients_rounded":[round(x,8) for x in agent.coeffs],
                 "choose_counts":dict(sorted(choice_counts.items()))},
        "synthetic_utility_mean_by_arm":{arm:round(statistics.mean(arr),8)
                         for arm,arr in utilities.items()},
        "synthetic_utility_median_by_arm":{arm:round(statistics.median(arr),8)
                         for arm,arr in utilities.items()},
        "abstentions_by_arm":abstentions,
        "learned_minus_balanced_mean":round(statistics.mean(delta),8),
        "learned_minus_balanced_positive_cases":sum(x>0 for x in delta),
        "learned_minus_balanced_negative_cases":sum(x<0 for x in delta),
        "learned_minus_balanced_equal_cases":sum(x==0 for x in delta),
        "shared_hard_guard_breaches":invalid,
        "oracle_upper_bound_breaches":oracle_upper_exceeded,
        "interpretation":"SIMULATED_OUTCOME_ONLY; NO_CAUSAL_HUMAN_EFFECT_OR_NONINFERIORITY",
    }
    report["report_sha256"] = canonical_sha(report)
    return report


def main()->int:
    ap=argparse.ArgumentParser(description="G4.9c train-only learned-model synthetic evaluation")
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result=benchmark()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("G49C_LEARNED_POLICY_SYNTHETIC_HOLDOUT_TECHNICAL_PASS")
    print("PROTOCOL="+result["protocol_commit"])
    print("TRAIN="+str(result["training_cases"])+" HOLDOUT="+str(result["heldout_cases"]))
    print("POLICY_COUNTS="+json.dumps(result["agent"]["choose_counts"],sort_keys=True))
    print("UTILITY_MEAN="+json.dumps(result["synthetic_utility_mean_by_arm"],sort_keys=True))
    print("DELEGATED_DELTA_VS_FIXED="+str(result["learned_minus_balanced_mean"]))
    print("COMMON_HARD_GUARD_BREACHES="+str(result["shared_hard_guard_breaches"]))
    print("REPORT_SHA256="+result["report_sha256"])
    print("HUMAN_N="+str(result["participant_count"])+" NONINFERIORITY="+result["noninferiority"])
    return 0


if __name__=="__main__":
    raise SystemExit(main())
