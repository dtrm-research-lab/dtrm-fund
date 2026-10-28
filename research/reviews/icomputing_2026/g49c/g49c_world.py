"""G4.9c seeded synthetic training worlds and independent simulated utility oracle.

Labels are not real economic outcomes; public cases strip them before fitting or
policy choice. Source visibility means the benchmark is NOT externally blinded.
"""
from __future__ import annotations
import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any

from g49c_agent import POLICY_ORDER, select_candidate

SEED = 20261029
TRAIN_N = 300
EVAL_N = 60
SCHEMA = "dtrm.ic.g49c.synthetic_independent_utility.v0"


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,allow_nan=False,
                    separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class World:
    public: dict[str, Any]
    # Outcomes are stored outside the PUBLIC case and never passed to the agent.
    realized_quality_by_id: dict[str, float]


def make_worlds() -> tuple[list[World], list[World]]:
    rng = random.Random(SEED)
    worlds: list[World] = []
    for n in range(TRAIN_N + EVAL_N):
        # Cases generated once; no picking or regeneration after observing outcomes.
        risk_weight = float(rng.choice((0,2,5,8,12)))
        candidates = []
        hidden = {}
        for j in range(5):
            cid = f"SIM{n:04d}_{j}"
            score = round(rng.uniform(50,100),4)
            risk = int(rng.randint(0,5))
            verified = bool(rng.random() > 0.10)
            blocked = bool(rng.random() < 0.07)
            candidates.append({"id":cid,"score":score,"risk":risk,
                               "verified":verified,"blocked":blocked})
            hidden[cid] = round(score + rng.gauss(0,9),6)
        public = {"id":f"TRAIN_{n:04d}" if n<TRAIN_N else f"EVAL_{n-TRAIN_N:04d}",
                  "risk_weight":risk_weight, "candidates":candidates}
        worlds.append(World(public,hidden))
    train=worlds[:TRAIN_N]
    evaluate=worlds[TRAIN_N:]
    ids_train={w.public["id"] for w in train}
    ids_eval={w.public["id"] for w in evaluate}
    if ids_train & ids_eval or len(ids_train)!=TRAIN_N or len(ids_eval)!=EVAL_N:
        raise AssertionError("Training and heldout scenario identity overlap")
    return train,evaluate


def oracle_utility(world:World, policy:str) -> float:
    candidate=select_candidate(world.public,policy)
    if candidate is None:
        return 0.0  # Protocol's explicit abstain utility, not invented after outcomes.
    cid=candidate["id"]
    return float(world.realized_quality_by_id[cid]
                 - world.public["risk_weight"]*candidate["risk"])


def training_rows(worlds:list[World]) -> list[tuple[dict[str,Any],dict[str,float]]]:
    if len(worlds)!=TRAIN_N or any(not x.public["id"].startswith("TRAIN_") for x in worlds):
        raise ValueError("Train-only training data required")
    return [(world.public,{p:oracle_utility(world,p) for p in POLICY_ORDER})
            for world in worlds]


def public_case_commitments(worlds:list[World]) -> dict[str,Any]:
    return {"scenario_count":len(worlds),
            "case_sha256":canonical_sha([w.public for w in worlds]),
            "oracle_sha256":canonical_sha([w.realized_quality_by_id for w in worlds])}
