"""G4.9c learned *offline* policy proposer. This is NOT an LLM autonomous agent.

Model input: PUBLIC features only, never the evaluation oracle's outcome labels.
Training gets utilities from separate training cases; test utility is inaccessible.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

import numpy as np

PROTOCOL_COMMIT = "333de0347f830dd7d581e992fcaa8fc905b04043"
POLICY_LIMITS = {"cautious": 2, "balanced": 4, "open": 5}
POLICY_ORDER = tuple(POLICY_LIMITS)
RIDGE_L2 = 0.01


def select_candidate(case: dict[str, Any], policy: str) -> dict[str, Any] | None:
    if policy not in POLICY_LIMITS:
        raise ValueError("Invalid admission policy")
    allowed = [c for c in case["candidates"]
               if c["verified"] and not c["blocked"]
               and isinstance(c["risk"], int) and c["risk"] <= 5
               and c["risk"] <= POLICY_LIMITS[policy]]
    if not allowed:
        return None
    return sorted(allowed, key=lambda c: (-float(c["score"]), str(c["id"])))[0]


def public_features(case: dict[str, Any], policy: str) -> tuple[float, ...]:
    """The policy-induced choice and user preference are visible to both arms."""
    winner = select_candidate(case, policy)
    w = float(case["risk_weight"])
    if winner is None:
        # Identical zero-utility abstention baseline is declared in protocol.
        return (1.0, 0.0, 0.0, w, 0.0, 0.0, 0.0)
    score = float(winner["score"])
    risk = float(winner["risk"])
    return (1.0, score/100.0, risk/5.0, w, w*risk/5.0,
            score*risk/500.0, 1.0)


@dataclass(frozen=True)
class LearnedPolicyAgent:
    coeffs: tuple[float, ...]
    train_count: int
    train_policy_rows: int

    def estimate(self, case: dict[str, Any], policy: str) -> float:
        return float(np.asarray(public_features(case, policy), dtype=float)
                     @ np.asarray(self.coeffs, dtype=float))

    def choose(self, case: dict[str, Any]) -> str:
        # Explicit tie-break: earlier fixed menu policy wins.
        estimates = [self.estimate(case, policy) for policy in POLICY_ORDER]
        return POLICY_ORDER[int(np.argmax(estimates))]


def fit(train: list[tuple[dict[str, Any], dict[str, float]]]) -> LearnedPolicyAgent:
    """Supervised ridge regression, only observed *training* utility labels."""
    if not train:
        raise ValueError("Training cases required")
    xs = []
    ys = []
    seen = set()
    for case, policy_utility in train:
        if case["id"] in seen:
            raise ValueError("Duplicate training scenario")
        seen.add(case["id"])
        if set(policy_utility) != set(POLICY_ORDER):
            raise ValueError("Training utility must cover all policies")
        for policy in POLICY_ORDER:
            xs.append(public_features(case, policy))
            ys.append(float(policy_utility[policy]))
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise ValueError("Nonfinite training rows")
    reg = RIDGE_L2 * np.eye(x.shape[1])
    reg[0, 0] = 0.0
    coefficients = np.linalg.solve(x.T @ x + reg, x.T @ y)
    if not np.isfinite(coefficients).all():
        raise ArithmeticError("Nonfinite coefficients")
    return LearnedPolicyAgent(tuple(float(v) for v in coefficients),
                              len(train), len(xs))
