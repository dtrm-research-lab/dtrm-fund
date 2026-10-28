"""G3.2 A3 original V0 VALID-only cutoff; NO original outcome or price access."""
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date
import unittest
from unittest.mock import patch

from ic_g3_2_a3_valid_only_cutoff import (
    N_VALID,ORIGINAL_Q25,OFFSET,matched_threshold,
    align_original_valid_keys_and_calibrated_p10,
    original_frozen_model_ordered_valid_rows,
    recheck_all_historical_price_hashes
)

SOURCE=Path(__file__).with_name("ic_g3_2_a3_valid_only_cutoff.py")

def validation_synthetic():
    n=N_VALID
    news=np.asarray([f"syn-news-{i}" for i in range(n)],dtype=object)
    # Weighted q25 source exactly matches frozen original P10 value.
    calibrated=np.full(n,ORIGINAL_Q25,dtype=np.float64)
    calibrated[:int(.25*n)-1]=ORIGINAL_Q25-.01
    raw=calibrated-OFFSET
    return news,raw

class A3OriginalValidOnlyTests(unittest.TestCase):
    def test_source_compiles(self):
        compile(SOURCE.read_text(),str(SOURCE),"exec")
    def test_no_old_outcome_or_bootstrap_paths(self):
        s=SOURCE.read_text()
        for token in ("read_pickle(bound","target_model",
                      "forward_excess_beta","cluster_bootstrap(",
                      "analyze_18_cells(", "to_pickle(", "np.save("):
            self.assertNotIn(token,s)
        self.assertIn('"old_forward_targets_opened":False',s)
        self.assertIn('"v2_v3_v4_model_outcome_comparisons_executed":False',s)
        self.assertIn('"any_bootstrap_executed":False',s)
    def test_explicit_authorization_required(self):
        s=SOURCE.read_text()
        for token in ("--authorize-a3-validation-only-volatility-calibration",
                      "--trust-original-audited-pickles",
                      "--acknowledge-price-provider-vintage-unverified",
                      "if not(a.authorize_a3_validation_only_volatility_calibration",
                      'must(not dest.exists()'):
            self.assertIn(token,s)
    def fake_pair_rows(self):
        ids,raw=validation_synthetic()
        native=pd.DataFrame({
            "news_id":ids,
            "ticker":["AAA" if i%2==0 else "BBB" for i in range(N_VALID)],
            "date_dt":pd.to_datetime(["2026-01-02"]*N_VALID,utc=True)
        })
        return native,raw
    def test_original_validation_all_19880_replay_and_q25(self):
        native,raw=self.fake_pair_rows()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"].to_numpy())
        self.assertAlmostEqual(q["0.25"],ORIGINAL_Q25,places=12)
        accepted,identity=align_original_valid_keys_and_calibrated_p10(
            native,native,native["news_id"].to_numpy(),raw,q)
        self.assertEqual(len(accepted),N_VALID)
        self.assertEqual(int(accepted.sum()),N_VALID-(int(.25*N_VALID)-1))
        self.assertTrue(identity["original_model_order_equals_archive_order"])
        self.assertEqual(identity["original_prediction_rows_reassigned_to_correct_native_keys"],0)
    def test_valid_original_model_legacy_row_permutation_remaps_predictions(self):
        native,raw=self.fake_pair_rows()
        # Original V0 model sorted rows, unlike original archived input order.
        perm=np.arange(N_VALID,dtype=int)[::-1]
        ordered=native.iloc[perm].reset_index(drop=True)
        model_raw=raw[perm]
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(model_raw,ordered["news_id"])
        accepted,identity=align_original_valid_keys_and_calibrated_p10(
            native,ordered,ordered["news_id"].to_numpy(),model_raw,q)
        expected=raw+OFFSET>=ORIGINAL_Q25
        self.assertTrue(np.array_equal(accepted,expected))
        self.assertFalse(identity["original_model_order_equals_archive_order"])
        self.assertEqual(identity["original_prediction_rows_reassigned_to_correct_native_keys"],
                         N_VALID)
    def test_wrong_model_score_news_vector_refused(self):
        native,raw=self.fake_pair_rows()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"])
        mistaken=native["news_id"].to_numpy().copy()
        mistaken[[0,1]]=mistaken[[1,0]]
        with self.assertRaisesRegex(RuntimeError,"prediction and frozen ordered key"):
            align_original_valid_keys_and_calibrated_p10(native,native,
                mistaken,raw,q)
    def test_missing_or_wrong_key_or_duplicate_refused(self):
        native,raw=self.fake_pair_rows()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"])
        changed=native.copy()
        changed.loc[7,"ticker"]="UNKNOWN_TICKER"
        with self.assertRaisesRegex(RuntimeError,"sets differ"):
            align_original_valid_keys_and_calibrated_p10(native,changed,
                changed["news_id"].to_numpy(),raw,q)
        repeated=native.copy()
        repeated.loc[7,["news_id","ticker"]]=repeated.loc[6,["news_id","ticker"]]
        with self.assertRaisesRegex(RuntimeError,"Duplicate"):
            align_original_valid_keys_and_calibrated_p10(native,repeated,
                repeated["news_id"].to_numpy(),raw,q)
    def test_event_date_mismatch_refused(self):
        native,raw=self.fake_pair_rows()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"])
        altered=native.copy()
        altered.loc[12,"date_dt"]=pd.Timestamp("2026-01-03",tz="UTC")
        with self.assertRaisesRegex(RuntimeError,"event dates differ"):
            align_original_valid_keys_and_calibrated_p10(native,altered,
                altered["news_id"].to_numpy(),raw,q)
    def test_nonunique_news_id_but_unique_composite_pair_supported(self):
        native,raw=self.fake_pair_rows()
        # Same news_id repeated for different tickers.
        native["news_id"]=[f"synthetic-{i//2}" for i in range(N_VALID)]
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"])
        perm=np.arange(N_VALID)[::-1]
        ordered=native.iloc[perm].reset_index(drop=True)
        admissible,proof=align_original_valid_keys_and_calibrated_p10(
            native,ordered,ordered["news_id"].to_numpy(),raw[perm],q)
        self.assertEqual(len(admissible),N_VALID)
        self.assertTrue(proof["identity_pairs_equal"])
        self.assertTrue(np.array_equal(admissible,
                                      raw+OFFSET>=ORIGINAL_Q25))
    def test_historical_frozen_q25_drift_refused(self):
        native,raw=self.fake_pair_rows()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,native["news_id"])
        q["0.25"]+=.0001
        with self.assertRaisesRegex(RuntimeError,"cutoff replay drift"):
            align_original_valid_keys_and_calibrated_p10(native,native,
                native["news_id"].to_numpy(),raw,q)
    def test_original_legacy_order_source_used_not_manual_sort(self):
        s=SOURCE.read_text()
        self.assertIn("from dtrm.legacy_model_rows import order_selected_legacy_rows",s)
        self.assertIn("order=order_selected_legacy_rows(",s)
        self.assertIn("full[\"ticker\"],full[\"date_dt\"],prior,selected",s)
        self.assertIn("align_original_valid_keys_and_calibrated_p10(",s)
        self.assertIn('"original_validation_model_archive_key_alignment":identity_proof',s)
        self.assertNotIn("sort_values(",s)
    def test_match_original_admission_with_weights_and_no_outcomes(self):
        ids=np.asarray([f"syn-news-{i}" for i in range(N_VALID)],dtype=object)
        risk=np.linspace(.001,.1,N_VALID,dtype=np.float64)
        admit=np.arange(N_VALID)<5000
        result,mask=matched_threshold(risk,ids,admit)
        self.assertEqual(result["common_validation_pairs"],N_VALID)
        self.assertAlmostEqual(result["original_p10_weighted_admission"],5000/N_VALID)
        self.assertAlmostEqual(result["volatility_weighted_admission"],5000/N_VALID)
        self.assertEqual(mask.dtype,np.dtype(bool))
    def test_tied_volatility_admission_difference_reported_not_hidden(self):
        ids=np.asarray([f"syn-news-{i}" for i in range(N_VALID)],dtype=object)
        risk=np.full(N_VALID,.02,dtype=float)
        admit=np.arange(N_VALID)<5000
        result,mask=matched_threshold(risk,ids,admit)
        self.assertEqual(int(mask.sum()),N_VALID)
        self.assertEqual(result["volatility_weighted_admission"],1.0)
        self.assertGreater(result["volatility_weighted_admission"],
                           result["original_p10_weighted_admission"])
    def test_invalid_validation_volatility_fails_closed(self):
        ids=np.arange(N_VALID).astype(object)
        vol=np.ones(N_VALID,dtype=float)*.02
        vol[200]=float("nan")
        with self.assertRaisesRegex(RuntimeError,"completeness drift"):
            matched_threshold(vol,ids,np.ones(N_VALID,dtype=bool))
    def test_price_root_is_sha_verified_before_pandas_pickle(self):
        # Security property is *execution order of deserialization*, NOT
        # import order: a helper defined above main legitimately imports
        # Pandas, but that helper is only INVOKED after all price hashes.
        import ast
        s=SOURCE.read_text()
        tree=ast.parse(s)
        main=next(n for n in tree.body
                  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
                  and n.name=="main")
        body=ast.get_source_segment(s,main)
        verify=body.index("prices=recheck_all_historical_price_hashes(")
        # Ensure the same call that checks all 174 price hashes occurs
        # before *every* original Pickle read on the main execution path.
        self.assertLess(verify,body.index("import pandas as pd"))
        self.assertLess(verify,body.index("pd.read_pickle("))
        self.assertLess(verify,body.index("original_frozen_model_ordered_valid_rows("))
        self.assertIn('sha(file)==item.get("sha256_new_local_commitment")',s)
        self.assertIn('and "/" not in filename and "\\\\" not in filename',s)
    def test_synthetic_source_report_and_price_vintage_binding(self):
        s=SOURCE.read_text()
        for txt in ("91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a",
                    '"original_price_vendor_acquisition_vintage_verified":False',
                    '"original_price_point_in_time_adjustments_verified":False',
                    '"risk_threshold_uses_validation_only":True',
                    '"a3_old_outcome_access_authorized":False'):
            self.assertIn(txt,s)
    def test_fixed_volatility_selection_and_19880_original_common_sample(self):
        s=SOURCE.read_text()
        self.assertIn("from ic_g2_g3_exploratory_core import trailing_volatility_60",s)
        self.assertIn('N_VALID=19880',Path(__file__).with_name("ic_g3_2_a3_numeric_source_quality_gate.py").read_text())
        self.assertIn("np.all(risk>=0)",s)
        self.assertIn('"original_p10_admitted_weighted_fraction"',s)
        self.assertIn('"volatility_admitted_weighted_fraction"',s)

if __name__=="__main__":
    unittest.main()
