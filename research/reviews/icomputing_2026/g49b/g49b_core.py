"""G4.9b bounded, offline human-authority pilot: deterministic core, no data collection.

NO real users in CI. No genuine LLM, finance return, trading or noninferiority test.
Signing verifies local record integrity only, not the identity of a human actor.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import random
import secrets
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "g49a"))
import g49a_mechanism as m  # existing strict synthetic selection engine

PROTOCOL_COMMIT = "7fbf67314f39f2bc7b9e34958dd3cbb38341ff3d"
SCHEMA = "dtrm.ic.g49b.consented_feasibility.v0"
FIXTURE_CANONICAL_SHA256 = "5c783b478fcab7c0dc8b5fb1a33f8d67588c9917a6e613302f0e3ed54f850a9c"
POLICIES = tuple(sorted(m.POLICIES))
ARMS = ("B_APPROVAL_REAL", "C_DIRECT_REAL")
FIXTURE_PATH = ROOT / "g49a" / "g49a_synthetic_cases.json"


class IntegrityFailure(ValueError):
    pass


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load_stimuli() -> list[dict]:
    # Reuses original *candidate inputs* only, not scripted 'human' decisions.
    root = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if set(root) != {"schema_version", "disclosure", "cases"}:
        raise IntegrityFailure("Unexpected fixture envelope")
    if root["disclosure"] != "SYNTHETIC_SCRIPTS_NOT_HUMAN_PARTICIPANTS":
        raise IntegrityFailure("Not the pinned synthetic fixture")
    cases = root["cases"]
    if sha(cases) != FIXTURE_CANONICAL_SHA256 or len(cases) != 12:
        raise IntegrityFailure("Fixture not identical to frozen G4.9a synthetic candidate set")
    for case in cases:
        m.validate_case(case)
    return cases


def assignment(session_id: str, key: bytes, cases: list[dict]) -> list[dict]:
    """Six B and six C; arm labels randomized within subject, not participant RCT."""
    if len(cases) != 12 or len({c["id"] for c in cases}) != 12:
        raise IntegrityFailure("Invalid crossover case set")
    if not isinstance(session_id, str) or len(session_id) < 16:
        raise IntegrityFailure("Session identifier invalid")
    if not isinstance(key, bytes) or len(key) < 32:
        raise IntegrityFailure("Key length too short")
    seed = int.from_bytes(hmac.digest(key, b"g49b-assign-v0|" + session_id.encode(), "sha256"), "big")
    rng = random.Random(seed)
    rows = list(cases)
    rng.shuffle(rows)
    arms = list(ARMS) * 6
    rng.shuffle(arms)
    return [{"case_id": case["id"], "arm": arm} for case, arm in zip(rows, arms)]


def issue_event(session_id: str, case_id: str, arm: str, decision: str,
                policy: str | None, nonce: str, key: bytes,
                now: int, ttl_seconds: int = 3600) -> dict:
    if arm not in ARMS or decision not in ("ACCEPT", "CHANGE", "CHOOSE", "REFUSE"):
        raise ValueError("Unknown decision")
    if (decision == "REFUSE") != (policy is None):
        raise ValueError("Refusal only with null policy")
    if policy is not None and policy not in m.POLICIES:
        raise ValueError("Non-menu policy")
    if not isinstance(session_id,str) or not session_id or not isinstance(case_id,str) or not case_id:
        raise ValueError("Context invalid")
    if not isinstance(nonce,str) or len(nonce)<24:
        raise ValueError("Nonce invalid")
    if type(now) is not int or type(ttl_seconds) is not int or ttl_seconds<1:
        raise ValueError("Time invalid")
    if len(key)<32:
        raise ValueError("Weak key")
    payload={"schema":SCHEMA,"session":session_id,"case":case_id,
             "arm":arm,"decision":decision,"policy":policy,"nonce":nonce,
             "issued_at":now,"expires_at":now+ttl_seconds}
    return {"payload":payload,"mac":hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()}


def verify_event(token: dict, key: bytes, expected_session: str, expected_case: str,
                 expected_arm: str, now: int, used_nonces: set[str]) -> dict:
    if not isinstance(token,dict) or set(token)!={"payload","mac"}:
        raise IntegrityFailure("Invalid event envelope")
    payload=token["payload"]
    if not isinstance(payload,dict) or set(payload)!={"schema","session","case","arm","decision","policy","nonce","issued_at","expires_at"}:
        raise IntegrityFailure("Invalid event shape")
    if not isinstance(token["mac"],str) or len(token["mac"])!=64:
        raise IntegrityFailure("Bad MAC")
    expected=hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, token["mac"]):
        raise IntegrityFailure("MAC mismatch")
    if (payload["schema"]!=SCHEMA or payload["session"]!=expected_session
        or payload["case"]!=expected_case or payload["arm"]!=expected_arm):
        raise IntegrityFailure("Wrong authority context")
    if (type(payload["issued_at"]) is not int or type(payload["expires_at"]) is not int
        or payload["issued_at"]>now or payload["expires_at"]<now):
        raise IntegrityFailure("Expired/future event")
    if payload["nonce"] in used_nonces:
        raise IntegrityFailure("Event nonce already used")
    if payload["decision"] not in ("ACCEPT","CHANGE","CHOOSE","REFUSE"):
        raise IntegrityFailure("Unknown authorized decision")
    if (payload["decision"]=="REFUSE") != (payload["policy"] is None):
        raise IntegrityFailure("Invalid refusal")
    if payload["policy"] is not None and payload["policy"] not in m.POLICIES:
        raise IntegrityFailure("Invalid policy")
    if expected_arm=="B_APPROVAL_REAL" and payload["decision"] not in ("ACCEPT","CHANGE","REFUSE"):
        raise IntegrityFailure("Not an approval-arm decision")
    if expected_arm=="C_DIRECT_REAL" and payload["decision"] not in ("CHOOSE","REFUSE"):
        raise IntegrityFailure("Not a direct-arm decision")
    used_nonces.add(payload["nonce"])
    return payload


def execute_authorized(case: dict, arm: str, session_id: str, token: dict,
                       key: bytes, now: int, used_nonces: set[str]) -> dict:
    m.validate_case(case)
    payload=verify_event(token,key,session_id,case["id"],arm,now,used_nonces)
    if payload["decision"]=="REFUSE":
        return {"status":"DENY_HUMAN_REFUSAL","selected":None,"policy":None}
    policy=payload["policy"]
    if payload["decision"]=="ACCEPT" and policy!=case["proposed_policy"]:
        raise IntegrityFailure("Accepted policy mismatches proposal")
    if payload["decision"]=="CHANGE" and policy==case["proposed_policy"]:
        raise IntegrityFailure("CHANGE did not change policy")
    selected=m._pick(case["candidates"],policy)
    if selected is None:
        return {"status":"ABSTAIN","selected":None,"policy":policy}
    return {"status":"EXECUTE","selected":selected,"policy":policy}


def score_proxy(case:dict, selected:str|None) -> float|None:
    if selected is None:return None
    c=next((x for x in case["candidates"] if x["id"]==selected),None)
    if c is None:raise IntegrityFailure("Unknown selected candidate")
    return float(c["score"])


def shadow(case:dict) -> dict:
    # Shared deterministic stub; *not* a deployed autonomous model.
    r=m.run_case(case,"A_DELEGATED")
    return {"status":r["status"],"selected":r["selected"],"policy":r["policy"],
            "score_proxy":score_proxy(case,r["selected"])}


def build_session(session_id: str, started_at: str, order: list[dict], rows: list[dict],
                  consenting_adult: bool) -> dict:
    if not consenting_adult or len(order)!=12 or len(rows)!=12:
        raise IntegrityFailure("Incomplete/unconsented session")
    if [ (r["case_id"],r["arm"]) for r in rows] != [(o["case_id"],o["arm"]) for o in order]:
        raise IntegrityFailure("Session rows do not correspond to randomized order")
    return {"schema":SCHEMA,"protocol_commit":PROTOCOL_COMMIT,
            "designation":"SELF_ATTESTED_ACTUAL_HUMAN_KEYBOARD_PARTICIPATION_NOT_ID_VERIFIED",
            "no_real_actions":True, "no_llm_in_autonomy_arm":True,
            "session":session_id,"started_at_utc":started_at,
            "consent":"ACTIVE_YES_AND_ADULT_YES","stimulus_sha":FIXTURE_CANONICAL_SHA256,
            "order":order,"rows":rows}
