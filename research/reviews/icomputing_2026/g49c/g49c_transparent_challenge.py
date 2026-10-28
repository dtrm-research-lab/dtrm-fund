"""G4.9c2 EXPLORATORY post-original transparent challenger; no human trial.

Read-only existing g49c modules; exact original seed first, then 32 additional
retrain-and-test synthetic generators. Never claims preregistered robustness.
The public synthetic data generating mechanism is score + mean-zero noise;
transparent policy maximizes score - risk_weight*risk, without outcome leakage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import Counter
from pathlib import Path

from g49c_agent import POLICY_ORDER, fit, select_candidate
from g49c_world import (EVAL_N, TRAIN_N, SEED, make_worlds, oracle_utility,
                         training_rows, World, canonical_sha)

ADDITIONAL_SEEDS = tuple(range(20261030, 20261062))


def transparent(case: dict) -> str:
    """Fixed pre-outcome score-risk rule; tie follows policy menu order."""
    predicted=[]
    for policy in POLICY_ORDER:
        chosen=select_candidate(case,policy)
        predicted.append(0.0 if chosen is None else float(
            chosen["score"] - case["risk_weight"]*chosen["risk"]))
    return POLICY_ORDER[predicted.index(max(predicted))]


def make_other_worlds(seed: int) -> tuple[list[World], list[World]]:
    """Exact generator algorithm copied from reviewed G4.9c source; new seed ONLY."""
    rng=random.Random(seed)
    worlds=[]
    for n in range(TRAIN_N + EVAL_N):
        risk_weight=float(rng.choice((0,2,5,8,12)))
        candidates=[]
        hidden={}
        for j in range(5):
            cid=f"SIM{n:04d}_{j}"
            score=round(rng.uniform(50,100),4)
            risk=int(rng.randint(0,5))
            verified=bool(rng.random()>0.10)
            blocked=bool(rng.random()<0.07)
            candidates.append({"id":cid,"score":score,"risk":risk,
                               "verified":verified,"blocked":blocked})
            hidden[cid]=round(score+rng.gauss(0,9),6)
        public={"id":f"TRAIN_{n:04d}" if n<TRAIN_N else f"EVAL_{n-TRAIN_N:04d}",
                "risk_weight":risk_weight,"candidates":candidates}
        worlds.append(World(public,hidden))
    return worlds[:TRAIN_N],worlds[TRAIN_N:]


def one_seed(seed:int) -> dict:
    if seed==SEED:
        train, test=make_worlds()
    else:
        train, test=make_other_worlds(seed)
    model=fit(training_rows(train))
    policies=Counter()
    vals={"LEARNED_DELEGATED":[],"TRANSPARENT_POLICY":[],"FIXED_BALANCED":[],
          "HINDSIGHT_CEILING":[]}
    differing=[]
    deltas=[]
    for world in test:
        case=world.public
        learned=model.choose(case)
        simple=transparent(case)
        policies[learned]+=1
        if learned!=simple:
            differing.append({"case":case["id"],"learned":learned,"transparent":simple,
                              "learned_synthetic_utility":oracle_utility(world,learned),
                              "transparent_synthetic_utility":oracle_utility(world,simple)})
        choices={"LEARNED_DELEGATED":learned,"TRANSPARENT_POLICY":simple,
                 "FIXED_BALANCED":"balanced",
                 "HINDSIGHT_CEILING":max(POLICY_ORDER,key=lambda p:oracle_utility(world,p))}
        for label,p in choices.items():
            vals[label].append(float(oracle_utility(world,p)))
        deltas.append(vals["TRANSPARENT_POLICY"][-1]-vals["LEARNED_DELEGATED"][-1])
    if sum(policies.values())!=EVAL_N or len(deltas)!=EVAL_N:
        raise AssertionError("Lost cases; refuse selective reporting")
    return {"seed":seed,"choice_counts":dict(sorted(policies.items())),
            "synthetic_mean":{k:round(statistics.mean(v),8) for k,v in vals.items()},
            "transparent_minus_learned_mean":round(statistics.mean(deltas),8),
            "different_policy_cases":len(differing),
            "different_cases_detail":differing,
            "transparent_better_cases":sum(d>0 for d in deltas),
            "learned_better_cases":sum(d<0 for d in deltas),
            "tied_cases":sum(d==0 for d in deltas)}


def challenge()->dict:
    original=one_seed(SEED)
    # The following assertions are reproducibility constraints from the
    # *already observed* G49c source, NOT model improvement goals.
    reference={"LEARNED_DELEGATED":83.45532793,
               "FIXED_BALANCED":80.81257747,
               "HINDSIGHT_CEILING":84.19572118}
    exact={name:abs(original["synthetic_mean"][name]-value)<1e-7
           for name,value in reference.items()}
    if not all(exact.values()):
        raise AssertionError("Original G4.9c source-level numerical reference mismatch")
    if original["different_policy_cases"]!=2:
        raise AssertionError("Original seed is not numerically reproduced")
    extra=[one_seed(s) for s in ADDITIONAL_SEEDS]
    d=[x["transparent_minus_learned_mean"] for x in extra]
    report={
        "status":"POST_OUTCOME_EXPLORATORY_SYNTHETIC_CHALLENGER_ONLY",
        "original_source_reproduced_eight_decimals":exact,
        "original":original,
        "post_outcome_seed_range":[min(ADDITIONAL_SEEDS),max(ADDITIONAL_SEEDS)],
        "post_outcome_additional_seeds":len(extra),
        "post_outcome_all_seeds":extra,
        "post_outcome_summary":{
            "transparent_minus_learned_mean_across_seeds":round(statistics.mean(d),8),
            "transparent_better_seeds":sum(x>0 for x in d),
            "learned_better_seeds":sum(x<0 for x in d),
            "tie_seeds":sum(x==0 for x in d),
            "average_differing_policies_per_60":statistics.mean(
                x["different_policy_cases"] for x in extra)},
        "real_human_participants":0,
        "actual_llm_comparators":0,
        "human_governance_noninferiority":"NOT_TESTED",
        "source_note":"Reproduces original modules; new seeded generator is a transparent source-level copy for EXPLORATORY challenge. NOT external outcome data.",
    }
    report["sha256"]=canonical_sha(report)
    return report


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=challenge()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("G49C2_EXPLORATORY_TRANSPARENT_CHALLENGER_REPLAY_PASS")
    print("REFERENCE="+str(result["original_source_reproduced_eight_decimals"]))
    print("ORIGINAL_MEANS="+json.dumps(result["original"]["synthetic_mean"],sort_keys=True))
    print("ORIGINAL_POLICY_DIFFERENCES="+str(result["original"]["different_policy_cases"]))
    print("EXTRA_SEEDS="+str(result["post_outcome_additional_seeds"]))
    print("EXTRA_SUMMARY="+json.dumps(result["post_outcome_summary"],sort_keys=True))
    print("HUMAN_N=0 NONINFERIORITY=NOT_TESTED")
    print("REPORT_SHA256="+result["sha256"])
    return 0


if __name__=="__main__":
    raise SystemExit(main())
