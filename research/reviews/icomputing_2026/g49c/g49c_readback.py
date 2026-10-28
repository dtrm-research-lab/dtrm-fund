"""G4.9c read-only private session verifier and synthetic-utility audit.

Never exports person-level records. Local operator can forge because it holds
the HMAC key: this is NOT independent proof of identity or valid field outcomes.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"g49b"))
from g49b_core import verify_event  # noqa: E402
from g49c_agent import PROTOCOL_COMMIT, fit, select_candidate  # noqa: E402
from g49c_participant import order_for  # noqa: E402
from g49c_world import make_worlds, training_rows, oracle_utility, canonical_sha, public_case_commitments  # noqa: E402

RECORD_FIELDS={"protocol_commit","schema","session","consent","designation",
               "no_financial_action","no_llm_model","public_eval_sha",
               "model_coefficients_sha","order","rows","started_at"}
ROW_FIELDS={"case_id","arm","proposed","decision","policy","status",
            "selected","elapsed_human_input_ms","event_token"}


class InvalidHumanRecord(ValueError):
    pass


def audit_one(path:Path,key:bytes) -> dict:
    try:
        envelope=json.loads(path.read_text(encoding="utf-8"))
        if type(envelope) is not dict or set(envelope)!={"record","hmac"}:
            raise InvalidHumanRecord("Unexpected envelope fields")
        record=envelope["record"]
        if type(record) is not dict or set(record)!=RECORD_FIELDS:
            raise InvalidHumanRecord("Unexpected fields (possibly personal information)")
        auth=hmac.new(key,json.dumps(record,sort_keys=True,separators=(",",":"),
                            ensure_ascii=True).encode(),hashlib.sha256).hexdigest()
        if type(envelope["hmac"]) is not str or not hmac.compare_digest(auth,envelope["hmac"]):
            raise InvalidHumanRecord("Session HMAC mismatch")
        if (record["protocol_commit"]!=PROTOCOL_COMMIT or
            record["schema"]!="dtrm.ic.g49c.consent_keyboard.v0" or
            record["consent"]!="YES_AND_ADULT_YES" or
            record["designation"]!="SELF_ATTESTED_REAL_KEYBOARD_NOT_IDENTITY_VERIFIED" or
            record["no_financial_action"] is not True or record["no_llm_model"] is not True):
            raise InvalidHumanRecord("Wrong protocol or consent state")
        sid=record["session"]
        if type(sid) is not str or len(sid)!=32 or any(c not in "0123456789abcdef" for c in sid) or path.name!=sid+".json":
            raise InvalidHumanRecord("Wrong session id")
        train, evals=make_worlds()
        agent=fit(training_rows(train))
        if record["public_eval_sha"]!=public_case_commitments(evals)["case_sha256"]:
            raise InvalidHumanRecord("Wrong test case set")
        if record["model_coefficients_sha"]!=canonical_sha([float(x) for x in agent.coeffs]):
            raise InvalidHumanRecord("Changed model coefficients")
        order=order_for(sid,key,[w.public for w in evals])
        if record["order"]!=order or len(record["rows"])!=12:
            raise InvalidHumanRecord("Wrong assignment/row count")
        byid={w.public["id"]:w for w in evals}
        used:set[str]=set()
        metrics=[]
        for row, assigned in zip(record["rows"],order):
            if type(row) is not dict or set(row)!=ROW_FIELDS:
                raise InvalidHumanRecord("Unexpected row data")
            if (row["case_id"],row["arm"])!=(assigned["id"],assigned["arm"]):
                raise InvalidHumanRecord("Wrong case/arm assignment")
            if type(row["elapsed_human_input_ms"]) is not int or row["elapsed_human_input_ms"]<0:
                raise InvalidHumanRecord("Invalid human-input duration")
            w=byid[row["case_id"]]
            proposed=agent.choose(w.public)
            if proposed!=row["proposed"]:
                raise InvalidHumanRecord("Agent proposal mismatch")
            token=row["event_token"]
            payload=verify_event(token,key,sid,row["case_id"],row["arm"],
                                 token["payload"]["issued_at"],used)
            if (payload["decision"],payload["policy"])!=(row["decision"],row["policy"]):
                raise InvalidHumanRecord("Mismatch signed and recorded choices")
            if row["arm"]=="B_APPROVAL_REAL":
                if payload["decision"]=="ACCEPT" and payload["policy"]!=proposed:
                    raise InvalidHumanRecord("Approving a different proposal")
                if payload["decision"]=="CHANGE" and payload["policy"]==proposed:
                    raise InvalidHumanRecord("No policy change despite CHANGE")
            decision=payload["decision"]
            policy=payload["policy"]
            actual=select_candidate(w.public,policy) if policy is not None else None
            selected=None if actual is None else actual["id"]
            status=("DENY_HUMAN_REFUSAL" if decision=="REFUSE"
                    else ("ABSTAIN" if actual is None else "EXECUTE"))
            if (status,selected)!=(row["status"],row["selected"]):
                raise InvalidHumanRecord("Unauthorized or mismatched decision output")
            actual_utility=oracle_utility(w,policy) if policy is not None else 0.0
            model_utility=oracle_utility(w,proposed)
            metrics.append({"arm":row["arm"],"decision":decision,
                            "status":status,"participant_synthetic_utility":actual_utility,
                            "learned_shadow_synthetic_utility":model_utility,
                            "elapsed_human_input_ms":row["elapsed_human_input_ms"]})
        return {"session_rows":12, "metrics":metrics}
    except InvalidHumanRecord:
        raise
    except (KeyError,TypeError,ValueError,IndexError,OverflowError) as exc:
        raise InvalidHumanRecord("Malformed or unverified session") from exc


def aggregate(path:Path,key:bytes)->dict:
    paths=sorted(path.glob("*.json"))
    if not paths:
        return {"status":"NO_CONSENTED_SESSIONS","sessions":0,"observed_rows":0}
    data=[audit_one(p,key) for p in paths]
    rows=[row for d in data for row in d["metrics"]]
    by_arm={}
    for arm in ("B_APPROVAL_REAL","C_DIRECT_REAL"):
        rr=[r for r in rows if r["arm"]==arm]
        by_arm[arm]={
            "task_count":len(rr),
            "decisions":dict(sorted(Counter(r["decision"] for r in rr).items())),
            "outcomes":dict(sorted(Counter(r["status"] for r in rr).items())),
            "human_mean_simulated_utility":statistics.mean(r["participant_synthetic_utility"] for r in rr),
            "agent_same_case_mean_simulated_utility":statistics.mean(r["learned_shadow_synthetic_utility"] for r in rr),
            "human_minus_agent_simulated_utility_mean":statistics.mean(
                r["participant_synthetic_utility"]-r["learned_shadow_synthetic_utility"] for r in rr),
            "median_keyboard_input_ms":statistics.median(r["elapsed_human_input_ms"] for r in rr)}
    return {"status":"SELF_ATTESTED_CONSENTED_CONVENIENCE_FEASIBILITY",
            "sessions":len(data),"observed_rows":len(rows),"by_arm":by_arm,
            "statistical_noninferiority":"NOT_TESTED",
            "real_welfare_or_trading_outcomes":"NOT_MEASURED",
            "actual_agent_is":"TRAINED_LINEAR_MODEL_NOT_LLM",
            "independent_identity":"NOT_VERIFIED",
            "source":"PRIVATE_RAW_RECORDS_NOT_UPLOADED"}


def main():
    import argparse
    from g49b_pilot import _private_root,_key
    p=argparse.ArgumentParser(description="Private-only G4.9c human/session readback")
    p.add_argument("--private-dir",type=Path,required=True)
    a=p.parse_args()
    root=_private_root(a.private_dir)
    result=aggregate(root,_key(root))
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
