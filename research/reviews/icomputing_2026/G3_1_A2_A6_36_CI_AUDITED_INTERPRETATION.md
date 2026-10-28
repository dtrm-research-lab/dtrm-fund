# G3.1 A2/A6 — audited 36 interval blocks and manuscript-safe interpretation

**Case:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Study stage:** **G3.1 A2/A6 original historical post-outcome exploratory comparison; empirical report QA PASS**  
**Original frozen protocol commit:** `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`  
**Tested scientific code commit:** `0c5e433f10ce742bc129b666dfc4551f4b2fd21b`

## Evidence lineage

The operator executed all original source and scientific gates and later the 18-cell full bootstrap runner. Source-only original cohort input manifest was SHA-matched; original q25/K10 published Phase II effects were reproduced by the corrected native-`float32` source precision method, with 71/71 prior source/synthetic tests PASS.

The operator reported the following immutable local JSON digests:

- G3.1 A2/A6 original **point-only report** SHA256:
  `8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb`.
- G3.1 A2/A6 original **full 10k news/ticker bootstrap report** SHA256:
  `53c4618f86f46a80a5a783c3449a8d120379f26c8d459c8e740dd4fb63697968`.

**New independent report-QA program (read-only):**
`ic_g3_1_a2_a6_full_report_qa.py`,
alongside its `test_ic_g3_1_a2_a6_full_report_qa.py`,
was operator-run after the original experiment on
`c4bee96b71764fb4bcd76eb20f09177bcf61ce06`
(a post-run QA code snapshot; it does not modify frozen science).
**Operator terminal confirms**:
`Ran 11 tests in 0.006s — OK`, then
`G3_1_A2_A6_FULL_36_CLUSTER_BLOCKS_REPORT_QA_PASS`.

Audit counted:

| Scope | Operator result |
| --- | ---: |
| All fixed original point cells unchanged in full report | 18/18 |
| Original sample feasible cells | 18/18 |
| All news + ticker CI blocks structurally valid | **36/36** |
| Blocks with any infeasible resampled Top-K | **0** |
| Cells with both news and ticker 95% intervals present | **18/18** |
| Cells with both **unadjusted mean** intervals excluding zero | **3/18 appearances** |
| Distinct policies among these three appearances | **2** |
| Unique policy–cohort configurations in full 18-cell grid | **15** |

The duplicated policies are **A2-q25/K10 = A6-q25/K10**
for each original cohort; the two prespecified work packages
report the same unchanged baseline policy three times.
**A2 V3 q25/K10 and A6 V3 K10 are ONE unique observation, NOT two independent replications.**

## Full original 18-cell intervals, mean delta forward-excess-beta

These source values are copied from the operator's accepted
full report QA terminal. Bounds are **nominal, unadjusted
95% percentile cluster-bootstrap confidence intervals**.
No inference holds that cluster news and ticker resamples are
independent experiments; they are two uncertainty approaches
on the same original observations.

| Work package | Cohort | Setting | Original Δmean | News-id 95% CI | Ticker 95% CI | Both exclude 0? |
| --- | --- | --- | ---: | --- | --- | --- |
| A2 | V2 | q15 | +0.07075341 | [+0.05014247, +0.08155493] | [-0.00802631, +0.08031646] | No |
| A2 | V2 | **q25** | +0.14429481 | [+0.12422081, +0.15296917] | [-0.00622022, +0.19615343] | No |
| A2 | V2 | q35 | +0.15356784 | [+0.13349940, +0.16234211] | [-0.00698984, +0.20751264] | No |
| A6 | V2 | K5% | +0.06548978 | [+0.03563277, +0.08516586] | [-0.03222756, +0.21500845] | No |
| A6 | V2 | **K10%** | +0.14429481 | [+0.12422081, +0.15296917] | [-0.00622022, +0.19615343] | No (same as A2 q25) |
| A6 | V2 | K15% | +0.05969969 | [+0.04856638, +0.08061432] | [-0.00894735, +0.16167829] | No |
| A2 | V3 | q15 | +0.09321596 | [+0.06957737, +0.11239979] | [-0.00574442, +0.11037348] | No |
| A2 | V3 | **q25** | +0.14943749 | [+0.12458648, +0.16903119] | **[+0.00792764, +0.19160254]** | **YES** |
| A2 | V3 | **q35** | +0.15372808 | [+0.12822758, +0.17339827] | **[+0.01122855, +0.19373854]** | **YES** |
| A6 | V3 | K5% | +0.09225000 | [+0.06235762, +0.12290583] | [-0.02686515, +0.21011202] | No |
| A6 | V3 | **K10%** | +0.14943749 | [+0.12458648, +0.16903119] | **[+0.00792764, +0.19160254]** | **YES (same as A2 q25)** |
| A6 | V3 | K15% | +0.07907292 | [+0.05548193, +0.09500486] | [-0.00053569, +0.16205617] | No |
| A2 | V4 | q15 | +0.01185918 | [+0.00998032, +0.01826862] | [-0.00676921, +0.03579278] | No |
| A2 | V4 | **q25** | +0.02756159 | [+0.02072872, +0.03240891] | [-0.00894309, +0.07024143] | No |
| A2 | V4 | q35 | +0.03298984 | [+0.02468463, +0.03655758] | [-0.00715741, +0.07577095] | No |
| A6 | V4 | K5% | +0.06165439 | [+0.05151425, +0.06693967] | [-0.00118509, +0.10459452] | No |
| A6 | V4 | **K10%** | +0.02756159 | [+0.02072872, +0.03240891] | [-0.00894309, +0.07024143] | No (same as A2 q25) |
| A6 | V4 | K15% | +0.01643478 | [+0.00970651, +0.02317965] | [-0.01915004, +0.05615306] | No |

All 18 news-cluster intervals have positive
lower bounds. Only the three V3 **appearances**
above have positive ticker-cluster lower bounds.
The 18 ticker bootstrap blocks are all structurally
valid, but only **three** exclude zero for the
mean effect; duplicate q25/K10 makes that
**two distinct observed policies**, both V3.
All 36 blocks had **zero** Top-K infeasible
bootstrap replicates in the operator report QA.

**Observed historical policy** (same A2 q25 and A6 K10):
- V2 `Δmean +0.14429480582475662`:
  ticker CI `[-0.006220224499702454, 0.19615343257319176]`,
  includes zero.
- V3 `Δmean +0.14943748898804188`:
  ticker CI `[0.007927639596164226, 0.1916025425540283]`,
  excludes zero (nominal, unadjusted).
- V4 `Δmean +0.027561593800783157`:
  ticker CI `[-0.008943087141960857, 0.07024142728187144]`,
  includes zero.

**Delta hit-rate** is a separate metric. For example,
V3 K15 ticker delta-mean CI includes zero
`[-0.0005356903886422511, 0.1620561682851985]`
even though its ticker delta-hit CI is positive
`[0.01120704194610901, 0.6715217391304344]`.
Do not relabel the hit-rate evidence as mean-effect
statistical evidence.

## Strict interpretation for reviewers

**Supported:** In already-seen historical data,
all fixed old-cohort comparisons show positive
point `forward_excess_beta` differences
versus an original no-P10-veto Top-K ranking.
Those effects are descriptively sensitive
to P10 quantile and Top-K capacity. All
36 nominal interval blocks computed and
passed the prewritten source/read-only QA.
Under news-id bootstrap, all 18 unadjusted
mean effect intervals exclude zero;
under ticker clustering, only V3 q25/K10
and V3 q35/K10 do (q25/K10 appears twice).

**Not supported:** Selecting q35 as statistically
better than q25 (two non-overlapping-policy
means require a paired **difference** interval;
their separately estimated overlapping CIs do
not test the contrast). Claiming fixed K10
universally optimal (V4 descriptively favors
K5). Treating two q25/K10 grid appearances
or dependent time/cohorts as independent
confirmations. Treating nominal CI95 exclusions
after testing 15 distinct configurations
and multiple outcome metrics as familywise
controlled evidence. Identifying historical
ticker-cluster inference as sufficient to
cover overlapping 60-day calendar dates.
Claiming a never-consulted, matured,
nonoverlapping new 60d prospective holdout.
Claiming original pre-event serialized
model boosters, point-in-time vendor
price vintage or capital-account realized
trading P&L.

The Phase II historical original outcomes
were already consulted before constructing
A2/A6 sensitivities. Label throughout as
**POST_OUTCOME_EXPLORATORY**, not
confirmatory preregistration.

## Manuscript-ready scientific language (English)

> In a prespecified retrospective sensitivity grid over the
> previously examined historical outcomes, we evaluated three
> fixed P10 admissibility thresholds (validation-derived q15,
> q25 and q35) and three Top-K selection fractions (5%, 10%
> and 15%) in each of V2, V3 and V4. All 18 appearances
> were feasible in the observed cohorts, and no bootstrap
> resample failed the required Top-K fill. Both news-id and
> ticker-cluster 10,000-replicate percentile intervals
> were available for all 18 appearances. The 18 news-id
> intervals for incremental mean 60-day forward
> beta-adjusted targets excluded zero, whereas ticker-cluster
> intervals excluded zero in only three appearances
> representing two distinct policy settings—q25/K10 and
> q35/K10, both in V3—because q25/K10 appears in both
> analytical work packages. Under ticker clustering,
> the original q25/K10 policy's nominal 95% interval
> included zero for V2 and V4, but not V3. These are
> unadjusted post-outcome exploratory intervals and
> cannot establish a prospective improvement, an
> optimal threshold/capacity, multiple-testing-controlled
> statistical superiority, or realizable portfolio
> investment returns.

## Next scientific options

1. **Close A2/A6 as exploratory analysis** with
   unadjusted results and the strict limitations
   above, with no additional historical outcome
   tuning. This is a scientifically defensible
   way to answer the sensitivity reviewer concerns.
2. Optionally design **another separately consented
   and prereviewed original-data reader** to compute
   direct paired q35−q25 contrasts, including ticker
   clustering and adjustment for multiple comparisons.
   This is *new analysis*, not already authorized
   by the 18-cell historical grid, and should not
   be used to select/rebrand a winning threshold.
3. Address the A3 historical price-vintage
   constraint separately; do not equate
   the current A2/A6 source authorization
   with A3, realized P&L or independent
   60d validation.

**Source for aggregate values:** operator-supplied
console report of original validated full JSON,
not a remotely opened copy of the user's original
private research data.
