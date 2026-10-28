"""Read-only, operator-local G4.9b audit. Never publishes participant rows.

A valid local HMAC establishes record integrity relative to the local issuer key,
NOT independent human identity, ethics approval, causal inference, or noninferiority.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from g49b_core import (ARMS, FIXTURE_CANONICAL_SHA256, PROTOCOL_COMMIT,
                        SCHEMA, assignment, canonical, execute_authorized,
                        load_stimuli, score_proxy, shadow, verify_event)

SESSION_FIELDS = frozenset({"schema","protocol_commit","designation",
        "no_real_actions","no_llm_in_autonomy_arm","session","started_at_utc",
        "consent","stimulus_sha","order","rows"})
ROW_FIELDS = frozenset({"case_id","arm","decision","policy","status","selected",
       "score_proxy","shadow_status","shadow_selected","shadow_policy",
       "shadow_score_proxy","elapsed_human_input_ms","event_token"})


class SessionAuditError(ValueError):
    pass


def audit_session(path: Path, key:bytes) -> dict:
    try:
        envelope=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(envelope,dict) or set(envelope)!={"record","hmac"}:
            raise SessionAuditError("Invalid session envelope")
        record=envelope["record"]
        if not isinstance(record,dict) or set(record)!=SESSION_FIELDS:
            raise SessionAuditError("Unexpected session fields; possible PII")
        expected=hmac.new(key,canonical(record),hashlib.sha256).hexdigest()
        if not isinstance(envelope["hmac"],str) or not hmac.compare_digest(envelope["hmac"],expected):
            raise SessionAuditError("Session HMAC mismatch")
        if (record["schema"]!=SCHEMA or record["protocol_commit"]!=PROTOCOL_COMMIT
            or record["stimulus_sha"]!=FIXTURE_CANONICAL_SHA256
            or record["designation"]!="SELF_ATTESTED_ACTUAL_HUMAN_KEYBOARD_PARTICIPATION_NOT_ID_VERIFIED"
            or record["consent"]!="ACTIVE_YES_AND_ADULT_YES"
            or record["no_real_actions"] is not True or record["no_llm_in_autonomy_arm"] is not True):
            raise SessionAuditError("Invalid source/designation/consent")
        sid=record["session"]
        if not isinstance(sid,str) or len(sid)!=32 or any(ch not in "0123456789abcdef" for ch in sid):
            raise SessionAuditError("Invalid pseudonymous ID")
        if path.name!=sid+".json":
            raise SessionAuditError("Session filename/context mismatch")
        cases=load_stimuli()
        order=assignment(sid,key,cases)
        if order!=record["order"] or len(record["rows"])!=len(order):
            raise SessionAuditError("Assignment/order mismatch")
        by_id={case["id"]:case for case in cases}
        used_nonces:set[str]=set()
        counts:Counter[str]=Counter()
        decisions:Counter[str]=Counter()
        paired: list[float]=[]
        missing=0
        interaction:dict[str,list[int]]={arm:[] for arm in ARMS}
        for row,expected_pair in zip(record["rows"],order):
            if not isinstance(row,dict) or set(row)!=ROW_FIELDS:
                raise SessionAuditError("Unexpected row fields, possible PII")
            if (row["case_id"],row["arm"])!=(expected_pair["case_id"],expected_pair["arm"]):
                raise SessionAuditError("Case/arm mismatch")
            if type(row["elapsed_human_input_ms"]) is not int or row["elapsed_human_input_ms"]<0:
                raise SessionAuditError("Invalid prompt time")
            case=by_id[row["case_id"]]
            token=row["event_token"]
            payload=verify_event(token,key,sid,case["id"],row["arm"],
                                 token["payload"]["issued_at"],used_nonces)
            if (payload["decision"],payload["policy"])!=(row["decision"],row["policy"]):
                raise SessionAuditError("Authorized decision and recorded decision differ")
            out=execute_authorized(case,row["arm"],sid,token,key,
                token["payload"]["issued_at"],set())  # separately revalidate token
            base=shadow(case)
            actual=(row["status"],row["selected"],row["policy"],row["score_proxy"])
            expected=(out["status"],out["selected"],out["policy"],score_proxy(case,out["selected"]))
            if actual!=expected:
                raise SessionAuditError("Recorded outcome contradicts authorized decision")
            if (row["shadow_status"],row["shadow_selected"],row["shadow_policy"],
                row["shadow_score_proxy"])!=(base["status"],base["selected"],base["policy"],base["score_proxy"]):
                raise SessionAuditError("Shadow outcome mismatch")
            decisions[(row["arm"],row["decision"])]+=1
            counts[(row["arm"],row["status"])]+=1
            interaction[row["arm"]].append(row["elapsed_human_input_ms"])
            if row["status"]=="EXECUTE" and base["status"]=="EXECUTE":
                paired.append(float(row["score_proxy"])-float(base["score_proxy"]))
            else:
                missing+=1
        return {"session_id":sid,"rows":len(order),"counts":counts,"decisions":decisions,
                "paired_score_deltas":paired,"unpaired_cases":missing,
                "elapsed_by_arm":interaction}
    except SessionAuditError:
        raise
    except (KeyError,TypeError,ValueError,IndexError,OverflowError) as exc:
        raise SessionAuditError("Malformed session or event") from exc


def aggregate_private(root:Path,key:bytes) -> dict:
    sessions=sorted(path for path in root.glob("*.json") if path.is_file())
    if not sessions:
        return {"designation":"NO_PARTICIPANTS_COLLECTED","sessions":0,"rows":0}
    audits=[audit_session(p,key) for p in sessions]
    if len({x["session_id"] for x in audits}) !=len(audits):
        raise SessionAuditError("Duplicate participant session IDs")
    counts:Counter=Counter()
    decisions:Counter=Counter()
    elapsed:dict[str,list[int]]={a:[] for a in ARMS}
    deltas=[]
    missing=0
    for item in audits:
        counts.update(item["counts"])
        decisions.update(item["decisions"])
        for arm in ARMS:elapsed[arm].extend(item["elapsed_by_arm"][arm])
        deltas.extend(item["paired_score_deltas"])
        missing+=item["unpaired_cases"]
    # Descriptive synthetic-score proxy only. Not an economic or noninferiority estimand.
    return {"designation":"SELF_ATTESTED_CONSENTED_OFFLINE_CONVENIENCE_FEASIBILITY",
            "sessions":len(audits),"rows":sum(x["rows"] for x in audits),
            "status_counts":{f"{a}|{s}":n for (a,s),n in sorted(counts.items())},
            "choice_counts":{f"{a}|{d}":n for (a,d),n in sorted(decisions.items())},
            "prompt_time_ms_median_by_arm":{a:statistics.median(v) if v else None
                                           for a,v in elapsed.items()},
            "paired_selected_score_difference_mean":(statistics.mean(deltas) if deltas else None),
            "paired_executed_cases":len(deltas),
            "unpaired_or_abstained_cases":missing,
            "notice":"ONLY_DISPLAYED_MODEL_SCORE_PROXY; NO_OUTCOME_UTILITY_OR_NONINFERIORITY"}


def main() -> int:
    import argparse
    from g49b_pilot import _key, _private_root
    ap=argparse.ArgumentParser(description="Private G4.9b read-only consented pilot audit")
    ap.add_argument("--private-dir",type=Path,required=True)
    args=ap.parse_args()
    root=_private_root(args.private_dir)
    result=aggregate_private(root,_key(root))
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    sys.exit(main())
