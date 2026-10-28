# G3.2 A3: source-only three-arm preflight

2026-10-28. ICOMPUTING-D-26-01069.

Original Mac operator V0 validation-only calibration:
56/56 tests PASS; source report SHA256
f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21.
P10 weighted admission 0.7503000595309957; V0 matched
60-return daily volatility cutoff 0.020823002555902668;
risk weighted admission 0.7514905485009868.
Different weighted rates result from threshold ties.
Original q25 P10 cutoff -0.16665692627429962.
No historical old outcome targets read in calibration.

Prepared, not yet executed:
ic_g3_2_a3_original_3arm_source_preflight.py
test_ic_g3_2_a3_original_3arm_source_preflight.py.
Code commit 30c470fa45268614dc26c869c93ec160d5323185.

This preflight binds all prior source report digests, 174
original July-5 price Pickle hashes, and three original
V2/V3/V4 signal file hashes. It reads no target Pickles.
It compares admission counts and K10 fill feasibility
for old frozen baseline, P10 q25 and V0-calibrated
volatility veto on the identical original cohort rows.
Its output is aggregated only: N, K, admitted counts,
intersections and whether each arm is full-K feasible.

Tests to run before any original source reads:
22 frozen pure-core + 12 numeric source + 17 V0 cutoff +
12 new A3 source-preflight tests = 63 local synthetic checks.
A separate operator-only original source access consent is
needed to run the preflight on SHA-audited Pickles.

No A3 target effects, old returns, bootstrap, historical
vendor vintage authentication, independent 60-day holdout,
or realized P&L authorized by this step.
No success is yet claimed for source preflight.
