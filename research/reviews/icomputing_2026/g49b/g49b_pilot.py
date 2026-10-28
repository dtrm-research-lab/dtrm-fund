#!/usr/bin/env python3
"""G4.9b offline *actual-keyboard* feasibility pilot. NO human data in CI.

Run only with voluntary adult consent and local research ethics/privacy review.
This is a CLI research prototype, not secure third-party participant authentication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from pathlib import Path

from g49b_core import (ARMS, POLICIES, PROTOCOL_COMMIT, assignment,
                        build_session, canonical, execute_authorized, issue_event,
                        load_stimuli, score_proxy, shadow)

ROOT_REPO = Path(__file__).resolve().parents[4]
PRIVATE_DEFAULT = Path.home() / ".local" / "share" / "dtrm-g49b-private"
NOTICE = """
G4.9b HUMAN CLAUSE — VOLUNTARY ADULT RESEARCH PILOT

You are invited to try 12 short, synthetic decision tasks on this computer.
This is a RESEARCH FEASIBILITY TEST, not investing advice or a real transaction.
You can refuse any decision and leave at any time without consequence.

What is shown: synthetic candidate ID, score and risk, and three allowed
risk policies. On half the tasks a deterministic agent STUB proposes one
policy for your approval; on the other half you choose independently.
Your selections, action/refusal status and seconds spent on each task will
be saved locally under a random session ID. There are no real companies,
real financial results, purchases or funds.

No name, email, address, free text or other identity is requested.
Your responses are pseudonymous, NOT necessarily anonymous to an organizer
who watches you operate the terminal. The session file is stored locally
outside GitHub in a private folder (mode 0700; file 0600), not uploaded.
The study organizer controls that computer and must explain retention,
privacy rights, optional withdrawal and any independent ethical review.
You can stop before completion without creating a completed session;
a saved session can be deleted using the withdraw command and its ID.
Copies already exported by an organizer need separate deletion.

This prototype cannot certify your identity, and its signed records
demonstrate local integrity, not independent third-party verification.
The automated comparator is a rule-based stub, NOT an autonomous LLM.

Participation is voluntary and strictly for adults aged at least 18.
"""


def _private_root(path: Path) -> Path:
    path = path.expanduser().resolve()
    if path.is_relative_to(ROOT_REPO):
        raise ValueError("PRIVATE storage must be outside the git repository")
    return path


def _mkdir_private(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("Do not use symlink private folder")
    mode = path.stat().st_mode & 0o777
    if mode & 0o077:
        raise ValueError("Private folder must not be accessible to group/others")


def _write_exclusive(path:Path, data:bytes) -> None:
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
    fd=os.open(str(path), flags,0o600)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _key(root:Path) -> bytes:
    p=root / ".issuer_hmac_key"
    if not p.is_file() or (p.stat().st_mode & 0o077):
        raise RuntimeError("Operator key missing or not private. Use init-key first.")
    key=bytes.fromhex(p.read_text(encoding="ascii").strip())
    if len(key)!=32:raise RuntimeError("Invalid operator HMAC key length")
    return key


def initialize(root:Path) -> None:
    _mkdir_private(root)
    path=root/".issuer_hmac_key"
    _write_exclusive(path,secrets.token_bytes(32).hex().encode("ascii")+b"\n")
    print("G49B_OPERATOR_PRIVATE_KEY_INITIALIZED")
    print("No participant records created.")
    print("The key protects local record integrity; it does NOT identify a person.")


def _ask(prompt:str, choices:set[str]) -> str:
    while True:
        a=input(prompt).strip().upper()
        if a=="QUIT":raise KeyboardInterrupt("Participant withdrew before completion")
        if a in choices:return a
        print("Invalid response; choose "+", ".join(sorted(choices))+" or QUIT.")


def _decision(case:dict, arm:str) -> tuple[str,str|None]:
    if arm=="B_APPROVAL_REAL":
        proposed=case["proposed_policy"]
        print("Stub proposal:",proposed)
        if proposed not in POLICIES:print("WARNING: proposal is not an allowed policy.")
        cmd=_ask("A=accept proposal, M=modify policy, R=refuse, QUIT=withdraw > ",{"A","M","R"})
        if cmd=="R":return "REFUSE",None
        if cmd=="A":
            if proposed not in POLICIES:
                print("Invalid proposal cannot be approved. Choose a valid modification.")
                policy=_ask("Choose CAUTIOUS/BALANCED/OPEN or QUIT > ",{p.upper() for p in POLICIES}).lower()
                return "CHANGE",policy
            return "ACCEPT",proposed
        policy=_ask("Choose CAUTIOUS/BALANCED/OPEN or QUIT > ",{p.upper() for p in POLICIES}).lower()
        if policy==proposed:
            print("No policy change. This will be recorded as ACCEPT.")
            return "ACCEPT",policy
        return "CHANGE",policy
    policy=_ask("Choose CAUTIOUS/BALANCED/OPEN; R=refuse; QUIT=withdraw > ",
                {p.upper() for p in POLICIES}|{"R"})
    return ("REFUSE",None) if policy=="R" else ("CHOOSE",policy.lower())


def run_enrollment(root:Path) -> str|None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Real participant CLI requires a human-operated TTY; tests are NOT participants")
    cases=load_stimuli()
    print(NOTICE)
    if _ask("Do you voluntarily consent? Type YES or NO > ",{"YES","NO"})!="YES":
        print("No consent; no participant session saved.")
        return None
    if _ask("Do you confirm you are at least 18? Type YES or NO > ",{"YES","NO"})!="YES":
        print("Not eligible; no participant session saved.")
        return None
    key=_key(root)
    sid=secrets.token_hex(16)
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    order=assignment(sid,key,cases)
    by_id={c["id"]:c for c in cases}
    used_nonces:set[str]=set()
    rows:list[dict]=[]
    try:
        for ix,entry in enumerate(order,1):
            case=by_id[entry["case_id"]]
            arm=entry["arm"]
            print(f"\nTask {ix}/12 — {case['id']} — {arm}")
            print("Menu: CAUTIOUS risk<=2, BALANCED risk<=4, OPEN risk<=5.")
            print("All arms forbid unverified, blocked or risk>5. Score is a model proxy, not true utility.")
            for candidate in case["candidates"]:
                print(f"  {candidate['id']}: score={candidate['score']}, risk={candidate['risk']},"
                      f" verified={candidate['verified']}, blocked={candidate['blocked']}")
            begin=time.monotonic()
            decision,policy=_decision(case,arm)
            duration_ms=max(0,round((time.monotonic()-begin)*1000))
            issued_at=int(time.time())
            token=issue_event(sid,case["id"],arm,decision,policy,
                              secrets.token_hex(16),key,issued_at)
            outcome=execute_authorized(case,arm,sid,token,key,issued_at,used_nonces)
            base=shadow(case)
            row={"case_id":case["id"],"arm":arm,"decision":decision,
                 "policy":policy,"status":outcome["status"],
                 "selected":outcome["selected"],"score_proxy":score_proxy(case,outcome["selected"]),
                 "shadow_status":base["status"],"shadow_selected":base["selected"],
                 "shadow_policy":base["policy"],"shadow_score_proxy":base["score_proxy"],
                 "elapsed_human_input_ms":duration_ms,
                 "event_token":token}
            rows.append(row)
            print("Result:",outcome["status"],outcome["selected"])
        session=build_session(sid,started,order,rows,consenting_adult=True)
        payload={"record":session,"hmac":hmac.new(key,canonical(session),hashlib.sha256).hexdigest()}
        p=root/(sid+".json")
        _write_exclusive(p,json.dumps(payload,indent=2,sort_keys=True).encode("utf-8")+b"\n")
        print("\nCOMPLETE: self-attested interactive session saved locally.")
        print("SESSION_ID="+sid)
        print("FILE="+str(p))
        print("Do not upload raw human-level files to GitHub or ChatGPT.")
        print(f"To withdraw locally: python3 {Path(__file__).name} withdraw --session-id {sid}")
        return sid
    except (KeyboardInterrupt,EOFError):
        print("\nStopped before completion; no participant session was saved.")
        return None


def withdraw(root:Path,sid:str) -> None:
    if len(sid)!=32 or any(x not in "0123456789abcdef" for x in sid):
        raise ValueError("Session ID must be the exact 32-char random hex code")
    p=root/(sid+".json")
    if not p.is_file():raise FileNotFoundError("Session not found")
    p.unlink()
    print("Local session file deleted; ask organizer about any previously exported copies.")


def main() -> int:
    os.umask(0o077)
    ap=argparse.ArgumentParser(description="G4.9b offline human-participation feasibility pilot")
    ap.add_argument("--private-dir",type=Path,default=PRIVATE_DEFAULT)
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init-key")
    sub.add_parser("enroll")
    rm=sub.add_parser("withdraw");rm.add_argument("--session-id",required=True)
    args=ap.parse_args()
    root=_private_root(args.private_dir)
    if args.cmd=="init-key":initialize(root)
    elif args.cmd=="enroll":run_enrollment(root)
    elif args.cmd=="withdraw":withdraw(root,args.session_id)
    return 0


if __name__=="__main__":
    sys.exit(main())
