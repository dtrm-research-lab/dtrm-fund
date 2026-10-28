"""G3.2 A3 original V0 VALID-only cutoff; NO original outcome or price access."""
import numpy as np
from pathlib import Path
from datetime import date
import unittest
from unittest.mock import patch

from ic_g3_2_a3_valid_only_cutoff import (
    N_VALID,ORIGINAL_Q25,OFFSET,matched_threshold,
    same_order_valid_and_calibrated_p10,
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
    def test_original_validation_all_19880_replay_and_q25(self):
        ids,raw=validation_synthetic()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        original=original_validation_p10_thresholds(raw,ids)
        self.assertEqual(original["0.25"],ORIGINAL_Q25)
        admitted=same_order_valid_and_calibrated_p10(ids,ids,raw,original)
        self.assertEqual(len(admitted),N_VALID)
        self.assertEqual(int(admitted.sum()),N_VALID-(int(.25*N_VALID)-1))
    def test_validation_row_order_permutation_refused(self):
        ids,raw=validation_synthetic()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,ids)
        other=ids.copy()
        other[[0,1]]=other[[1,0]]
        with self.assertRaisesRegex(RuntimeError,"model-row order"):
            same_order_valid_and_calibrated_p10(ids,other,raw,q)
    def test_historical_frozen_q25_drift_refused(self):
        ids,raw=validation_synthetic()
        from ic_g2_g3_exploratory_core import original_validation_p10_thresholds
        q=original_validation_p10_thresholds(raw,ids)
        q["0.25"]+=.0001
        with self.assertRaisesRegex(RuntimeError,"cutoff replay drift"):
            same_order_valid_and_calibrated_p10(ids,ids,raw,q)
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
        s=SOURCE.read_text()
        self.assertIn("recheck_all_historical_price_hashes(",s)
        self.assertLess(s.index("prices=recheck_all_historical_price_hashes("),
                        s.index("import pandas as pd"))
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
        self.assertIn('and risk>=0',s.replace("risk>=0","and risk>=0"))
        self.assertIn('"original_p10_admitted_weighted_fraction"',s)
        self.assertIn('"volatility_admitted_weighted_fraction"',s)

if __name__=="__main__":
    unittest.main()
