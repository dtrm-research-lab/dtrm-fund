# G3.1 q25/K10 — original Phase II mean precision remediation, pending operator proof

**Case:** ICOMPUTING-D-26-01069
**Event:** 2026-10-28
**Scientific status:** Existing G2 frozen, G3.0 model source PASS, G3.1 preanalysis old Phase II parity **BLOCKED**, no 18-cell A2/A6 sensitivity results yet.

## Original old code versus protected old code: verified operator findings

Original source commit:
`c7502a690162459cdfb3413573e3133c42efb126`.
Original Phase II primary bootstrap experiment:
`research/experiments/run_phase2_primary_bootstrap.py`.
Original `evaluate_selection` calls
`old_frame["target_model"].to_numpy()` and applies
`float(target[indices].mean())` with the native saved-array
dtype. The original code on original SHA-verified local
source files reproduced the preexisting point effects at
**exact float equality**.

Earlier protected code at approved immutable commit
`5cf62c854643576ee6059ac44f55a805b8ff3137`
was validated by **38/38** synthetic/static tests
before the owner authorized historical `point` run.
It subsequently returned:
`ScientificGateError: Old historical q25/K10 effect failed 1e-12 parity`.

**Operator's independent three-cohort diagnostic** on
the existing original source data returned:

| Cohort | Original = preexisting expected delta_mean | New protected delta_mean | Delta hit identical? |
| --- | ---: | ---: | --- |
| V2, N=4,449, K=444 | 0.14429480582475662 | 0.14429479716387619 | YES |
| V3, N=2,827, K=282 | 0.14943748898804188 | 0.14943749220804015 | YES |
| V4, N=40,320, K=4,032 | 0.027561593800783157 | 0.027561596978355536 | YES |

The original frozen original Phase II evaluator and
original frozen historic published expected values
match for every old cohort, but **the new protected
implementation diverges at ~3e-9–9e-9** in means.
No ranker mask/hit-rate discrepancy was observed.
The original sensitivity calculation aborted before
constructing the 18 new cells.

**Most plausible cause (not yet empirically confirmed
on local original source dtype):** original Phase II
`pandas.Series.to_numpy()` retains original
`float32` target source dtype and `np.mean` rounds
inside `float32` before conversion to Python float.
The new G3.1 guard extracted `target_model` with
`to_numpy(dtype=float)` and the pure engine
converted `_vec(target,dtype=np.float64)`, which
calculates a mathematically close but **not
bitwise/rounding-identical** mean. A standalone
synthetic float32 test reproduces a mean delta
difference of the same order, but does not by
itself prove the private original source's dtype.

## Minimal implementation repair, no policy modifications

- `ic_g3_1_a2_a6_join_contract.py`:
  `extract_source_arrays` now retains original
  numeric `target_model` source dtype in memory,
  exactly like frozen Phase II, instead of
  automatically converting to float64.
- `ic_g2_g3_exploratory_core.py`:
  `select_topk` and `cluster_bootstrap` now
  preserve floating source target dtype for
  `np.mean`, while remaining strict about
  nonfinite values and all original mask/rank/K
  and bootstrapping policies. Integer synthetic
  labels are still promoted safely for tests.
- No original V2/V3/V4 `.pkl`, scientific model
  weight, raw date, source SHA, original q25
  cutoff, original published effect, sample
  membership, selected ranker iteration,
  K policy, uncertainty seed or returned
  financial outcome was edited.
- Synthetic regression additions:
  original source join must preserve float32
  in `extract_source_arrays`, and pure
  `select_topk` and resampling must
  reproduce the original float32-mean
  delta *exactly* rather than an upcast mean.
- Revised original-only diagnostic adds
  `--candidate-source-commit` to independently
  bind these corrections to the operator-tested
  source and prints original vs protected
  target dtype as aggregate metadata.

This changes an **implementation precision defect**,
not the frozen scientific experimental design.
It must be documented in manuscript provenance
as a post-hoc *reproducibility correction*, not
claim true prospective preregistration.

## Safe local decision procedure — TEST BEFORE ORIGINAL DATA

The `G3.1` 18-cell old-outcome runner, by original
scientific contract, remains OFF.

1. Run ALL **40** current synthetic/static release
   tests (previously 38 + two float32 regressions)
   plus **9** current synthetic/static diagnostic
   tests (previously 8 + original/protected
   dtype check) on the latest immutable Git SHA.
2. Before reading any old historical original
   `target_model` values, the revised
   diagnostic must be consented to
   independently and SHA-bound to the same
   new scientific code commit, together
   with the frozen original Phase II
   `load_cohort/evaluate_selection`.
3. It may report only V2/V3/V4 already-published
   original q25/K10 point-effect deltas,
   numeric types and pair/source counts.
   No new q15/q35 thresholds, A6 new K
   cells, any bootstrap or A3 prices.
4. **If 40 or 9 tests fail or the three-cohort
   new parity is NOT exact at 1e-12, STOP**.
   Do not relax tolerance or adjust original
   published expected numbers.
5. Only a separate later explicitly consented
   A2/A6 `--mode point` attempt can
   produce new 18-cell historical results
   after this diagnostic exact parity PASS.

**No results or source tests beyond the operator's
earlier 38/38 PASS are claimed in this
source-remediation document.**
