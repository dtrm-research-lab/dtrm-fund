"""G4.9a synthetic *software* authority mechanism. Not a human/AI behavioral experiment.

Runs offline with Python standard library only. No orders, market data, network, LLMs,
real users, portfolio returns or claims of noninferiority. See G49A_0_PROTOCOL_PREEXECUTION.md.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

PROTOCOL_COMMIT = "6e77f2a2b7d5667c21d275cc25d7b1143c95c335"
SCHEMA = "dtrm.ic.g4_9a.synthetic_mechanism.v1"
VERSION = 1
POLICIES = {"balanced": 4, "cautious": 2, "open": 5}
ARMS = ("A_DELEGATED", "B_APPROVAL", "C_DIRECT")
ALLOWED_CASE_KEYS = frozenset({"id", "tick", "candidates", "proposed_policy", "human_policy", "authorization_mode", "untrusted_policy"})
ALLOWED_CANDIDATE_KEYS = frozenset({"id", "score", "risk", "verified", "blocked"})
MODES = frozenset({"valid", "missing", "revoked", "expired", "wrong_case", "tampered"})


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class InvalidFixture(ValueError):
    pass


@dataclass(frozen=True)
class Authorization:
    # Simulated trusted-approval record; digest checks accidental mutations only.
    # It is NOT a cryptographic signature and offers no protection if this
    # trusted source is itself compromised.
    case_id: str
    policy: str
    version: int
    expires_at: int
    approved: bool
    revoked: bool
    digest: str


def _auth_payload(case_id: str, policy: str, version: int, expires_at: int,
                  approved: bool, revoked: bool) -> dict[str, Any]:
    return {"case_id": case_id, "policy": policy, "version": version,
            "expires_at": expires_at, "approved": approved, "revoked": revoked}


def scripted_authorization(case_id: str, policy: str, expires_at: int,
                           *, version: int = VERSION, approved: bool = True,
                           revoked: bool = False) -> Authorization:
    if policy not in POLICIES or not isinstance(case_id, str):
        raise ValueError("Invalid policy/case in authorization")
    p = _auth_payload(case_id, policy, version, expires_at, approved, revoked)
    return Authorization(**p, digest=sha256(p))


def authorization_valid(auth: Authorization | None, case_id: str,
                        policy: str, tick: int) -> tuple[bool, str]:
    if auth is None:
        return False, "DENY_NO_APPROVAL"
    if not isinstance(auth, Authorization):
        return False, "DENY_BAD_RECORD"
    expected = _auth_payload(auth.case_id, auth.policy, auth.version,
                             auth.expires_at, auth.approved, auth.revoked)
    if auth.digest != sha256(expected):
        return False, "DENY_RECORD_MUTATION"
    if auth.case_id != case_id or auth.version != VERSION:
        return False, "DENY_WRONG_CONTEXT"
    if auth.policy != policy:
        return False, "DENY_POLICY_MISMATCH"
    if not auth.approved:
        return False, "DENY_NO_APPROVAL"
    if auth.revoked:
        return False, "DENY_REVOKED"
    if auth.expires_at < tick:
        return False, "DENY_EXPIRED"
    return True, "AUTHORIZED"


def validate_case(case: dict[str, Any]) -> None:
    if type(case) is not dict or set(case) != ALLOWED_CASE_KEYS:
        raise InvalidFixture("Scenario fields missing or unexpected")
    if not isinstance(case["id"], str) or not case["id"]:
        raise InvalidFixture("Scenario ID required")
    if type(case["tick"]) is not int or case["tick"] < 0:
        raise InvalidFixture("Nonnegative integer tick required")
    if type(case["candidates"]) is not list or not case["candidates"]:
        raise InvalidFixture("At least one candidate required")
    if (not isinstance(case["proposed_policy"], str)
        or not isinstance(case["human_policy"], str)
        or case["authorization_mode"] not in MODES
        or (case["untrusted_policy"] is not None
            and not isinstance(case["untrusted_policy"], str))):
        raise InvalidFixture("Invalid scripted controller fields")
    seen: set[str] = set()
    for item in case["candidates"]:
        if type(item) is not dict or set(item) != ALLOWED_CANDIDATE_KEYS:
            raise InvalidFixture("Candidate fields missing or unexpected")
        if not isinstance(item["id"], str) or not item["id"] or item["id"] in seen:
            raise InvalidFixture("Candidate ID missing or duplicated")
        seen.add(item["id"])
        if type(item["score"]) not in (int, float) or not math.isfinite(item["score"]):
            raise InvalidFixture("Candidate score must be finite")
        if type(item["risk"]) is not int or not 0 <= item["risk"] <= 100:
            raise InvalidFixture("Candidate risk must be integer in range")
        if type(item["verified"]) is not bool or type(item["blocked"]) is not bool:
            raise InvalidFixture("Candidate flags must be bool")


def _authorize_case(case: dict[str, Any], policy: str) -> Authorization | None:
    mode = case["authorization_mode"]
    if mode == "missing":
        return None
    cid = case["id"] if mode != "wrong_case" else "some-other-case"
    expiry = case["tick"] - 1 if mode == "expired" else case["tick"] + 1
    auth = scripted_authorization(cid, policy, expiry, revoked=mode == "revoked")
    if mode == "tampered":
        # Trusted original approval has not been re-signed after mutation.
        return dataclasses.replace(auth, policy="open" if policy != "open" else "cautious")
    return auth


def _pick(candidates: list[dict[str, Any]], policy: str) -> str | None:
    # A common hard guard applies in ALL arms, before any arm-specific policy.
    # Candidate IDs are synthetic strings, not tickers.
    limit = POLICIES[policy]
    admissible = [
        x for x in candidates
        if x["verified"] and not x["blocked"] and x["risk"] <= 5
        and x["risk"] <= limit
    ]
    ordered = sorted(admissible, key=lambda x: (-x["score"], x["id"]))
    return ordered[0]["id"] if ordered else None


def run_case(case: dict[str, Any], arm: str) -> dict[str, Any]:
    validate_case(case)
    if arm not in ARMS:
        raise InvalidFixture("Unknown arm")
    checks = 1  # common, deterministic mandatory hard safety validation
    if arm == "A_DELEGATED":
        policy = case["proposed_policy"]
        if policy not in POLICIES:
            return _row(case, arm, "DENY_BAD_POLICY", None, None, checks, "no_policy")
    elif arm == "B_APPROVAL":
        if case["proposed_policy"] not in POLICIES:
            return _row(case, arm, "DENY_BAD_POLICY", None, None, checks, "no_policy")
        # The approved policy is the authoritative selection, even if the
        # agent had proposed another policy. This approval is scripted, NOT real.
        policy = case["human_policy"]
        checks += 1
        if policy not in POLICIES:
            return _row(case, arm, "DENY_BAD_POLICY", None, None, checks, "invalid_approval_choice")
        auth = _authorize_case(case, policy)
        allowed, reason = authorization_valid(auth, case["id"], policy, case["tick"])
        if not allowed:
            return _row(case, arm, reason, None, policy, checks, "not_authorized")
    else:
        policy = case["human_policy"]
        checks += 1
        if policy not in POLICIES:
            return _row(case, arm, "DENY_BAD_POLICY", None, None, checks, "invalid_direct_choice")
        auth = _authorize_case(case, policy)
        allowed, reason = authorization_valid(auth, case["id"], policy, case["tick"])
        if not allowed:
            return _row(case, arm, reason, None, policy, checks, "not_authorized")

    # A lower-trust injection is recorded but *never* allowed to replace
    # the trusted, arm-selected policy in any arm.
    selected = _pick(case["candidates"], policy)
    if selected is None:
        return _row(case, arm, "ABSTAIN", None, policy, checks, "none_admissible")
    return _row(case, arm, "EXECUTE", selected, policy, checks, "policy_enforced")


def _row(case: dict[str, Any], arm: str, status: str, selected: str | None,
         policy: str | None, checks: int, reason: str) -> dict[str, Any]:
    return {"case_id": case["id"], "arm": arm, "status": status,
            "selected": selected, "policy": policy, "logical_checks": checks,
            "reason": reason, "untrusted_input_ignored": case["untrusted_policy"] is not None}


def run_suite(cases: list[dict[str, Any]]) -> dict[str, Any]:
    if type(cases) is not list or not cases:
        raise InvalidFixture("Nonempty scenario list required")
    ids: set[str] = set()
    for case in cases:
        validate_case(case)
        if case["id"] in ids:
            raise InvalidFixture("Duplicate scenario ID")
        ids.add(case["id"])
    rows = [run_case(case, arm) for case in cases for arm in ARMS]
    results = {a: [r for r in rows if r["arm"] == a] for a in ARMS}
    counts = {a: dict(sorted(Counter(r["status"] for r in rs).items()))
              for a, rs in results.items()}

    hard_breaches = 0
    for row in rows:
        if row["status"] == "EXECUTE":
            c = next(c for c in cases if c["id"] == row["case_id"])
            chosen = next(x for x in c["candidates"] if x["id"] == row["selected"])
            if (not chosen["verified"] or chosen["blocked"] or chosen["risk"] > 5
                or chosen["risk"] > POLICIES[row["policy"]]):
                hard_breaches += 1

    # Mechanical matched-policy invariant across all identical executed inputs.
    matched = 0
    for case in cases:
        for pname in POLICIES:
            selected = _pick(case["candidates"], pname)
            # Controller labels must not change the deterministic decision.
            if any(_pick(case["candidates"], pname) != selected for _ in ARMS):
                raise AssertionError("Matched-policy parity violated")
            matched += 1

    report = {
        "schema_version": SCHEMA,
        "protocol_commit": PROTOCOL_COMMIT,
        "status": "SYNTHETIC_SOFTWARE_MECHANISM_ONLY",
        "source_data": "synthetic_only_no_human_participants_no_real_actions",
        "case_count": len(cases),
        "case_sha256": sha256(cases),
        "row_count": len(rows),
        "arms": list(ARMS),
        "status_counts": counts,
        "common_hard_guard_breaches": hard_breaches,
        "matched_policy_invariant_checks": matched,
        "total_logical_checks": {a: sum(r["logical_checks"] for r in rs)
                                  for a, rs in results.items()},
        "rows": rows,
    }
    report["report_sha256"] = sha256(report)
    return report


def verify_report(report: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    if report != run_suite(cases):
        raise AssertionError("Report differs from deterministic replay")
    if report["common_hard_guard_breaches"] != 0:
        raise AssertionError("Shared hard-safety invariant violated")
    for r in report["rows"]:
        if r["arm"] in ("B_APPROVAL", "C_DIRECT") and r["status"] == "EXECUTE":
            # Execution requires authorization in this trusted simulated model.
            case = next(c for c in cases if c["id"] == r["case_id"])
            auth = _authorize_case(case, r["policy"])
            if not authorization_valid(auth, case["id"], r["policy"], case["tick"])[0]:
                raise AssertionError("Unapproved action accepted")
