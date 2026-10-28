"""Synthetic-only test suite for the G3.1 original phase II join.

NEVER imports old private prices, saved Pickles or outcome files.
"""
import unittest
import numpy as np
import pandas as pd
from pathlib import Path
from ic_g3_1_a2_a6_join_contract import (
    source_exact_join,extract_source_arrays,OriginalJoinError,Q25,OFFSET,
)

def fixture(n=2827):
    news=[f"N{i}" for i in range(n)]
    tickers=["A" if i%2 else "B" for i in range(n)]
    time=pd.date_range("2026-06-11",periods=n,freq="min",tz="UTC")
    raw=np.linspace(-.3,0.,n)
    cal=raw+OFFSET
    sig=pd.DataFrame({
        "news_id":news,"ticker":tickers,"date_dt":time,
        "baseline_prediction":np.linspace(0,1,n),
        "p10_raw":raw,"p10_calibrated":cal,
        "p10_pass":cal>=Q25,
    })
    targets=pd.DataFrame({
        "news_id":news,"ticker":tickers,"date_dt":time,
        "target_model":np.sin(np.arange(n)/10.)
    })
    return sig,targets

class ProtectedOriginalSourceJoinTests(unittest.TestCase):
    def test_valid_2827_original_shape_one_to_one(self):
        sig,tgt=fixture()
        out=source_exact_join(sig,tgt,"V3")
        self.assertEqual(len(out),2827)
        self.assertEqual(out.iloc[0]["news_id"],"N0")
        data=extract_source_arrays(out)
        self.assertEqual(len(data["target"]),2827)
        self.assertTrue(np.array_equal(data["original_q25_pass"],sig["p10_pass"]))
    def test_partial_pair_join_refused(self):
        sig,tgt=fixture()
        tgt.loc[0,"news_id"]="different"
        with self.assertRaisesRegex(OriginalJoinError,"Missing original"):
            source_exact_join(sig,tgt,"V3")
    def test_duplicate_signal_pair_refused(self):
        sig,tgt=fixture()
        sig.loc[1,["news_id","ticker"]]=sig.loc[0,["news_id","ticker"]]
        with self.assertRaisesRegex(OriginalJoinError,"Duplicate original"):
            source_exact_join(sig,tgt,"V3")
    def test_duplicate_target_pair_refused(self):
        sig,tgt=fixture()
        tgt.loc[1,["news_id","ticker"]]=tgt.loc[0,["news_id","ticker"]]
        with self.assertRaisesRegex(OriginalJoinError,"Duplicate original"):
            source_exact_join(sig,tgt,"V3")
    def test_null_news_id_refused(self):
        sig,tgt=fixture()
        sig.loc[0,"news_id"]=None
        with self.assertRaisesRegex(OriginalJoinError,"Null original"):
            source_exact_join(sig,tgt,"V3")
    def test_wrong_row_cardinality_refused(self):
        sig,tgt=fixture()
        with self.assertRaisesRegex(OriginalJoinError,"Unexpected original"):
            source_exact_join(sig.iloc[:-1],tgt,"V3")
    def test_wrong_cohort_refused(self):
        sig,tgt=fixture()
        with self.assertRaises(OriginalJoinError):
            source_exact_join(sig,tgt,"V1")
    def test_mismatched_timestamp_refused(self):
        sig,tgt=fixture()
        tgt.loc[10,"date_dt"]=pd.Timestamp("2026-06-01",tz="UTC")
        with self.assertRaisesRegex(OriginalJoinError,"timestamps differ"):
            source_exact_join(sig,tgt,"V3")
    def test_bad_timestamp_refused(self):
        sig,tgt=fixture()
        sig["date_dt"]=sig["date_dt"].astype(object)
        sig.at[0,"date_dt"]="not-a-date"
        with self.assertRaisesRegex(OriginalJoinError,"timestamps differ"):
            source_exact_join(sig,tgt,"V3")
    def test_nonfinite_target_refused(self):
        sig,tgt=fixture()
        tgt.loc[1,"target_model"]=float("nan")
        with self.assertRaisesRegex(OriginalJoinError,"Nonfinite original"):
            source_exact_join(sig,tgt,"V3")
    def test_nonfinite_rank_refused(self):
        sig,tgt=fixture()
        sig.loc[0,"baseline_prediction"]=float("inf")
        with self.assertRaisesRegex(OriginalJoinError,"Nonfinite original"):
            source_exact_join(sig,tgt,"V3")
    def test_calibration_offset_drift_refused(self):
        sig,tgt=fixture()
        sig.loc[0,"p10_calibrated"]+=0.002
        with self.assertRaisesRegex(OriginalJoinError,"offset numeric"):
            source_exact_join(sig,tgt,"V3")
    def test_q25_flag_drift_refused(self):
        sig,tgt=fixture()
        sig.loc[0,"p10_pass"]=not bool(sig.loc[0,"p10_pass"])
        with self.assertRaisesRegex(OriginalJoinError,"decision flag mismatch"):
            source_exact_join(sig,tgt,"V3")
    def test_not_boolean_p10_source_refused(self):
        sig,tgt=fixture()
        sig["p10_pass"]=sig["p10_pass"].map(str)
        with self.assertRaisesRegex(OriginalJoinError,"strict Boolean"):
            source_exact_join(sig,tgt,"V3")
    def test_original_float32_target_dtype_preserved_after_join(self):
        sig,tgt=fixture()
        tgt["target_model"]=tgt["target_model"].astype(np.float32)
        joined=source_exact_join(sig,tgt,"V3")
        data=extract_source_arrays(joined)
        self.assertEqual(data["target"].dtype,np.dtype("float32"))
        self.assertTrue(np.array_equal(data["target"],
                                       tgt["target_model"].to_numpy()))
    def test_no_io_or_autorun_in_join_module(self):
        s=Path(__file__).with_name("ic_g3_1_a2_a6_join_contract.py").read_text()
        for forbidden in ("read_pickle","to_pickle","pd.read_csv(","pickle.load",
                          "np.load(","open(","sys.argv","argparse.ArgumentParser"):
            self.assertNotIn(forbidden,s)
if __name__=="__main__":
    unittest.main()
