#!/usr/bin/env python3
"""IC G1.2k — seal historical numeric reproduction evidence (read-only).

Reads locally generated historical JSON audit reports and hashes four
UNAPPROVED reconstructed XGBoost model binaries. No Pickle, .npy, news
text, market target/price, model inference or training is read/executed.
Produces a small path-redacted evidence manifest; *NOT* authorization
for independent temporal holdout or provenance closure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
NAMES={
    "preflight": "IC_G1_2_preflight.json",
    "rebuild": "IC_G1_2_rebuild.json",
    "row_parity": "IC_G1_2_row_parity.json",
    "source_subset": "IC_G1_2_source_subset.json",
    "feature_provenance": "IC_G1_2_feature_provenance.json",
    "text_provenance": "IC_G1_2_text_provenance.json",
    "embedding_inventory": "IC_G1_2_embedding_inventory.json",
    "supplement_schema": "IC_G1_2_supplement_schema.json",
    "embedding_parity": "IC_G1_2_embedding_parity.json",
}
STATES={
    "preflight": "PRECHECK_ONLY",
    "rebuild": "HISTORICAL_AGGREGATE_PARITY_ONLY",
    "row_parity": "HISTORICAL_NUMERIC_PARITY_PASS_PROVENANCE_PENDING",
    "source_subset": "CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING",
    "feature_provenance": "HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN",
    "text_provenance": "TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN",
    "embedding_inventory": "G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED",
    "supplement_schema": "G1_2I_SUPPLEMENT_NAMED_SCHEMA_READY_FOR_PREDECLARED_MAPPING",
    "embedding_parity": "G1_2J_HISTORICAL_384_EMBEDDING_ROW_PARITY_PASS",
}
MODELS=("exante_ranker.ubj","p10.ubj","p50.ubj","p90.ubj")

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda:stream.read(1024*1024),b""):
            h.update(piece)
    return h.hexdigest()

def must(condition: bool, reason: str):
    if not condition:
        raise RuntimeError(reason)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports-dir",required=True)
    parser.add_argument("--models-dir",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    root=Path(args.reports_dir).expanduser()
    models_root=Path(args.models_dir).expanduser()
    out=Path(args.out).expanduser()
    if out.exists():
        parser.error("Refusing to overwrite an existing sealed report")
    reports={}
    report_hashes={}
    for key,name in NAMES.items():
        path=root/name
        must(path.is_file() and not path.is_symlink(),
             "Missing historical audit JSON: "+name)
        reports[key]=json.loads(path.read_text(encoding="utf-8"))
        report_hashes[name]=digest(path)
        actual=reports[key].get("status")
        must(actual==STATES[key],f"Historical {key} audit status mismatch: {actual}")
    pre=reports["preflight"]["preflight"]
    must(pre.get("historical_commit_verified") is True and
         pre.get("can_begin_historical_reconstruction") is True,
         "Pinned historic preflight not validated")
    rebuild=reports["rebuild"]
    must(rebuild.get("frozen_source_commit")==PIN,"Wrong model reconstruction source commit")
    checks=rebuild.get("reconstruction",{}).get("checks",{})
    must(len(checks)==12 and all(x is True for x in checks.values()),
         "G1.2 frozen historical reconstruction not 12/12 PASS")
    original_candidate_hashes=rebuild["reconstruction"]["candidate_model_sha256"]
    saved_hashes={}
    for name in MODELS:
        path=models_root/name
        must(path.is_file() and not path.is_symlink(),
             "Reconstructed candidate booster unavailable: "+name)
        sha=digest(path)
        must(sha==original_candidate_hashes.get(name),
             "Local reconstructed booster hash changed: "+name)
        saved_hashes[name]=sha
    row=reports["row_parity"]
    must(row.get("source_pin")==PIN and row.get("frozen_rows")==40320
         and row.get("frozen_features")==390,"Wrong original V1 row-parity scope")
    rank=row["baseline_numeric_parity"]
    must(rank.get("max_abs_difference")==0.0 and
         rank.get("rows")==40320 and rank.get("exceeding_tolerance")==0,
         "Original ex-ante ranker not numerically identical")
    num=row["p10_numeric_parity_candidates"]
    for name,limit in (("p10_raw",0.0),("p10_calibrated",1e-6)):
        report=num.get(name,{})
        must(report.get("rows")==40320 and
             report.get("within_tolerance") is True and
             report.get("exceeding_tolerance")==0 and
             report.get("max_abs_difference") is not None and
             report["max_abs_difference"]<=limit,
             "Original 40,320-row P10 numeric gate failed: "+name)
    veto=row["p10_veto_parity"]
    first=veto["v1_absolute_p10_veto"]
    must(first.get("disagreements")==0 and
         first.get("exact_pass_match") is True and first.get("original_pass")==0
         and first.get("reconstructed_pass")==0,
         "Frozen original V1 veto decisions mismatch")
    must(veto.get("disagreements")==0 and
         veto.get("exact_pass_match") is True and veto.get("original_pass")==23348
         and veto.get("reconstructed_pass")==23348,
         "Frozen original V4 veto decisions mismatch")
    subset=reports["source_subset"]
    must(subset["BRK_B_canonicalized_membership"]["selected_keys_missing_in_raw"]==0
         and subset["BRK_B_canonicalized_membership"]["selected_keys_present_in_raw"]==40320,
         "Original 40,320-row canonical key membership was not complete")
    fp=reports["feature_provenance"]
    must(fp.get("canonical_pair_membership_all") is True and
         fp.get("canonical_signal_order_is_raw_subsequence") is True and
         fp["beta_to_feature_column390"].get("alignment_type")==
         "KEYED_BY_NEWS_AND_CANONICAL_TICKER" and
         fp["beta_to_feature_column390"].get("max_absolute_difference")==0.0 and
         fp["beta_to_feature_column390"].get("matching_all_40320") is True,
         "Historical pair-order/keyed-beta corroboration incomplete")
    text=reports["text_provenance"]
    must(text.get("rows_compared")==40320 and
         text.get("text_feature_columns")==5 and
         text.get("max_abs_difference")==0.0 and
         text.get("rows_exceeding_1e_6")==0,
         "Historical text features not 40,320x5 exact")
    inventory=reports["embedding_inventory"]
    must(inventory.get("manifest_missing_signal_news")==0 and
         inventory.get("manifest_additional_news")==0 and
         inventory.get("unique_signal_news_ids")==5526 and
         inventory.get("manifest_exact_labels_and_counts")=={
            "2026-06-06":4764,"2026-05-23":735,"v1_supplement":27},
         "Historical 5,526 news-source cache inventory mismatch")
    supplement=reports["supplement_schema"]
    must(supplement.get("recognized_schema_only_ready") is True and
         supplement.get("manifest_supplement_news_count")==27,
         "Original V1 27-ID supplemental mapping incomplete")
    embed=reports["embedding_parity"]
    full=embed["all_40320x384_parity"]
    must(embed.get("frozen_training_commit")==PIN and
         embed.get("historic_signal_rows")==40320 and
         embed.get("embedding_dimensions")==384 and
         full.get("rows")==40320 and
         full.get("coordinates")==15482880 and
         full.get("coordinates_bitwise_equal")==15482880 and
         full.get("max_abs_difference")==0.0 and
         full.get("rows_exceeding_1e_6")==0 and
         full.get("coordinates_exceeding_1e_6")==0 and
         full.get("tolerance_pass") is True,
         "Original V1 384-dimensional embedding numerical replay incomplete")
    expected_source_rows={
        "2026-06-06":35358,"2026-05-23":4753,"v1_supplement":209}
    for label,n in expected_source_rows.items():
        check=embed["per_source_row_parity"].get(label,{})
        must(check.get("rows")==n and check.get("tolerance_pass") is True
             and check.get("max_abs_difference")==0.0,
             "Historical original-source embedding cohort mismatch: "+label)
    dossier={
        "schema_version":"dtrm.ic.g1.historical_parity_dossier.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":"HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN",
        "source_commit":PIN,
        "orig_model_weights_recovered":False,
        "model_weight_lineage":"Retrospective exact-result reconstruction, not original serialized booster weights",
        "historical_sources_scope":"V1/V4 already consumed; not a new untouched holdout",
        "original_independently_committed_v1_sha256":{
            "features":"a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750",
            "signals":"dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b",
            "beta":"e39896db92f1bb7c8334f61a6eee7bc71f8acbd6b6e87504c388ae0b8b1463d8",
        },
        "local_json_report_sha256":report_hashes,
        "reconstructed_unapproved_model_sha256":saved_hashes,
        "validated_historical_counts":{
            "signal_rows":40320,
            "features_per_row":390,
            "source_embedding_unique_news":5526,
            "embedding_coordinates_exact":15482880,
            "text_coordinates_exact":40320*5,
            "keyed_beta_coordinates_exact":40320,
            "all_input_coordinates_numerically_reproduced":40320*390,
            "ranker_rows_max_abs_difference":0.0,
            "p10_raw_rows_max_abs_difference":num["p10_raw"]["max_abs_difference"],
            "p10_calibrated_rows_max_abs_difference":num["p10_calibrated"]["max_abs_difference"],
            "v4_relative_veto_disagreements":0,
            "v1_absolute_veto_disagreements":0,
        },
        "scientific_remaining_gates":{
            "raw_candidate_filename_row_count_discrepancy":"OPEN: 265145 local vs 40320 historical V1 contract",
            "original_raw_to_v1_selection_filter_lineage":"OPEN",
            "fresh_independent_temporal_cohort_preregistered":"NO",
            "new_horizon_60day_labels_inspected":"NO",
            "new_scientific_model_comparison_authorized":"NO",
        },
        "not_included":"No scientific Pickles, vector values, raw news, market prices, target labels or per-row predictions",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(dossier,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2k:",dossier["status"])
    print("Validated historical input coordinates:",40320*390)
    print("Sealed reports:",len(report_hashes),"; reconstructed candidate models:",len(saved_hashes))
    print("Historic source commit:",PIN)
    print("Remaining: source filtering/file cardinality OPEN; independent temporal test NOT AUTHORIZED")
    print("Dossier path:",out)
    print("Dossier SHA256:",digest(out))
    print("No historical/future scientific raw data opened.")
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G1.2k halted: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
