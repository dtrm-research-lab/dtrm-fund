"""G4.9c optional *real keyboard* pilot launcher, offline synthetic tasks.

No enrollment in CI. Research ethics/privacy signoff needed before recruitment.
The proposer is a TRAINED LINEAR MODEL, NOT an LLM. Outcomes are simulated.
No claims of actual welfare, noninferiority, or verified human identity.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import hmac
import json
import os
import random
import secrets
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"g49b"))
from g49b_pilot import (_private_root, _mkdir_private, _write_exclusive,
                       _key, initialize)  # noqa: E402
from g49b_core import issue_event, verify_event  # noqa: E402
from g49c_agent import POLICY_ORDER, PROTOCOL_COMMIT, fit, select_candidate  # noqa: E402
from g49c_world import (make_worlds, training_rows, canonical_sha,
                         public_case_commitments)  # noqa: E402

PRIVATE_DEFAULT=Path.home()/".local"/"share"/"dtrm-g49c-private"
ARMS=("B_APPROVAL_REAL","C_DIRECT_REAL")
NOTICE="""G4.9c HUMAN CLAUSE — OPTIONAL VOLUNTARY ADULT PILOT (SYNTHETIC TASKS)
No money, investment, goods or accounts are involved. You will see 12 artificial
ranking choices and risk policies. Half the tasks let you approve/change/refuse
a proposal by a TRAINED LINEAR MODEL (not an LLM); in the others you choose
without seeing that proposal. You may stop at any time without penalty.
The system logs each typed choice, response time and symbolic outcome under
a random session ID, locally with file permissions 0600. No name/email/free
text is requested. No data are uploaded. The operator controls the device,
may identify you by observation and must describe retention/withdrawal rights.
Synthetic future outcomes are not shown and are not real financial utility.
The issuer and participant run on one device: the HMAC does not prove identity.
External ethics/privacy review is required before recruiting real people.
"""


def order_for(session_id:str,key:bytes,eval_public:list[dict]) -> list[dict]:
    if len(eval_public)!=60:raise ValueError("60 synthetic evaluation cases required")
    rng=random.Random(int.from_bytes(hmac.digest(key,
        b"g49c-participant-assignment-v0|"+session_id.encode(),"sha256"),"big"))
    chosen=list(eval_public)
    rng.shuffle(chosen)
    arms=list(ARMS)*6
    rng.shuffle(arms)
    return [{"id":c["id"],"arm":a} for c,a in zip(chosen[:12],arms)]


def _ask(q:str, allowed:set[str])->str:
    while True:
        v=input(q).strip().upper()
        if v=="QUIT":raise KeyboardInterrupt("Voluntary withdrawal")
        if v in allowed:return v
        print("Choose one of:",", ".join(sorted(allowed)),"or QUIT")


def _choose(arm:str, proposed:str)->tuple[str,str|None]:
    menu={p.upper() for p in POLICY_ORDER}
    if arm=="B_APPROVAL_REAL":
        v=_ask("A=approve proposal, M=modify, R=refuse, QUIT=leave > ",{"A","M","R"})
        if v=="R":return "REFUSE",None
        if v=="A":return "ACCEPT",proposed
        p=_ask("Choose CAUTIOUS/BALANCED/OPEN > ",menu).lower()
        return ("ACCEPT",p) if p==proposed else ("CHANGE",p)
    v=_ask("Choose CAUTIOUS/BALANCED/OPEN or R=refuse > ",menu|{"R"})
    return ("REFUSE",None) if v=="R" else ("CHOOSE",v.lower())


def enroll(private:Path)->str|None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Real participant enrollment requires an actual TTY")
    print(NOTICE)
    if _ask("Voluntary consent? YES/NO > ",{"YES","NO"})!="YES":
        print("No consent; no session created.");return None
    if _ask("Are you at least 18? YES/NO > ",{"YES","NO"})!="YES":
        print("Not eligible; no session created.");return None
    train,evals=make_worlds()
    model=fit(training_rows(train))
    key=_key(private)
    sid=secrets.token_hex(16)
    order=order_for(sid,key,[w.public for w in evals])
    lookup={w.public["id"]:w.public for w in evals}
    used_nonces:set[str]=set()
    rows=[]
    try:
        for idx,task in enumerate(order,1):
            case=lookup[task["id"]]
            arm=task["arm"]
            proposed=model.choose(case)
            print(f"\n{idx}/12 {case['id']} — {arm}")
            print("Objective: synthetic quality minus risk weight × candidate risk.")
            print(f"Your assigned risk-weight: {case['risk_weight']:.0f}")
            print("Menu: cautious risk<=2; balanced risk<=4; open risk<=5.")
            print("Safety excludes unverified, blocked, and risk>5 candidates.")
            for c in case["candidates"]:
                print(c["id"],"score=",c["score"],"risk=",c["risk"],
                      "verified=",c["verified"],"blocked=",c["blocked"])
            if arm=="B_APPROVAL_REAL":print("Learned-model proposed policy:",proposed)
            started=time.monotonic()
            decision,policy=_choose(arm,proposed)
            elapsed=max(0,round((time.monotonic()-started)*1000))
            t=int(time.time())
            token=issue_event(sid,case["id"],arm,decision,policy,
                              secrets.token_hex(16),key,t)
            verify_event(token,key,sid,case["id"],arm,t,used_nonces)
            if decision=="ACCEPT" and policy!=proposed:
                raise ValueError("Approved rule differs from proposed rule")
            if decision=="CHANGE" and policy==proposed:
                raise ValueError("CHANGE must differ from proposal")
            winner=select_candidate(case,policy) if policy is not None else None
            status=("DENY_HUMAN_REFUSAL" if decision=="REFUSE"
                    else ("ABSTAIN" if winner is None else "EXECUTE"))
            rows.append({"case_id":case["id"],"arm":arm,"proposed":proposed,
                         "decision":decision,"policy":policy,"status":status,
                         "selected":None if winner is None else winner["id"],
                         "elapsed_human_input_ms":elapsed,"event_token":token})
            print("Result:",status,rows[-1]["selected"])
        record={"protocol_commit":PROTOCOL_COMMIT,
                "schema":"dtrm.ic.g49c.consent_keyboard.v0",
                "session":sid,"consent":"YES_AND_ADULT_YES",
                "designation":"SELF_ATTESTED_REAL_KEYBOARD_NOT_IDENTITY_VERIFIED",
                "no_financial_action":True,"no_llm_model":True,
                "public_eval_sha":public_case_commitments(evals)["case_sha256"],
                "model_coefficients_sha":canonical_sha([float(x) for x in model.coeffs]),
                "order":order,"rows":rows,
                "started_at":dt.datetime.now(dt.timezone.utc).isoformat()}
        envelope={"record":record,
                  "hmac":hmac.new(key,json.dumps(record,sort_keys=True,
                         separators=(",",":"),ensure_ascii=True).encode(),
                         hashlib.sha256).hexdigest()}
        target=private/(sid+".json")
        _write_exclusive(target,(json.dumps(envelope,indent=2,sort_keys=True)+"\n").encode())
        print("SAVED PRIVATE SESSION ID:",sid)
        print("For local removal: withdraw --session-id",sid)
        print("Do not share raw participant records or the private issuer key.")
        return sid
    except (KeyboardInterrupt,EOFError):
        print("Exit before completing all tasks. No completed session saved.")
        return None


def main():
    import argparse
    os.umask(0o077)
    p=argparse.ArgumentParser(description="G4.9c voluntary offline keyboard pilot (no real outcomes)")
    p.add_argument("--private-dir",type=Path,default=PRIVATE_DEFAULT)
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init-key")
    sub.add_parser("enroll")
    w=sub.add_parser("withdraw");w.add_argument("--session-id",required=True)
    a=p.parse_args()
    root=_private_root(a.private_dir)
    if a.cmd=="init-key":initialize(root)
    elif a.cmd=="enroll":enroll(root)
    else:
        sid=a.session_id
        if len(sid)!=32 or any(x not in "0123456789abcdef" for x in sid):
            raise ValueError("Invalid session id")
        (root/(sid+".json")).unlink()
        print("Local participant session removed; organizer must remove external copies.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
