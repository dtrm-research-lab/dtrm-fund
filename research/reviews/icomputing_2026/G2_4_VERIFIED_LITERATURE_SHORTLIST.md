# G2.4 — Verified literature shortlist for Reviewer #2 comment 8

Date 2026-10-27. Status `REFERENCES_VERIFIED_FROM_PUBLISHER_OR_INDEX_SOURCE_NOT_YET_ADDED_TO_MANUSCRIPT`.

This is an initial **shortlist**, NOT an exhaustive literature review,
and the following literature DOES NOT provide missing HDPG independent
temporal evidence. Each entry has externally checked title, year and DOI
(or the original conference proceedings), and a narrowly accurate
reason for citing it. No invented publication claims.

## Finance and economic significance

**Gu, S., Kelly, B., and Xiu, D. (2020).**
"Empirical Asset Pricing via Machine Learning."
*The Review of Financial Studies*, 33(5), 2223–2273.
DOI: `10.1093/rfs/hhaa009`.
Publisher: https://academic.oup.com/rfs/article/33/5/2223/5758276

Relevance: ML risk-premium forecasting and economically evaluated
benchmark portfolios. Provides context for why HDPG's statistical
`forward_excess_beta` comparison must be clearly distinguished
from implementable investment P&L. Does **not** itself validate
HDPG or any of its selected holdings.

## Transparent/controlled decision design

**Rudin, C. (2019).**
"Stop explaining black box machine learning models for high stakes
decisions and use interpretable models instead."
*Nature Machine Intelligence*, 1, 206–215.
DOI: `10.1038/s42256-019-0048-x`.
Publisher: https://www.nature.com/articles/s42256-019-0048-x

Relevance: High-stakes decisions and transparency of decision
processes. This work advocates intrinsically interpretable
models; HDPG's interpretable outer control does **not**
make its internal XGBoost predictors inherently interpretable.
Avoid equating a deterministic policy layer with full
interpretability.

## Risk-coverage and abstention baseline

**Geifman, Y., and El-Yaniv, R. (2017).**
"Selective Classification for Deep Neural Networks."
*Advances in Neural Information Processing Systems*, 30.
Publisher: https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html
Related preprint DOI: `10.48550/arXiv.1705.08500`.

Relevance: Risk–coverage trade-offs and rejection/abstention
rules provide intellectual context for capacity/acceptance
trade-offs in a risk-aware selector. It is NOT a
financial-ranking empirical benchmark and does not
establish HDPG's comparative value over volatility filters.

## Human/AI complementarity versus human-specified rules

**Gonzalez, C., Donahue, K., Goldstein, D. G., Heidari, H.,
Jalali, M. S., Schelble, B., Singh, A., and Woolley, A. W. (2026).**
"Toward a science of human-AI teaming for decision making:
A complementarity framework."
*PNAS Nexus*, 5(3), pgag030 (2026).
DOI: `10.1093/pnasnexus/pgag030`.
Publication metadata:
https://pubmed.ncbi.nlm.nih.gov/41834945/

Relevance: Genuine human-AI complementarity requires separate
evidence comparing humans alone, AI alone, and their
combination (or a well-specified causal setup). This is
conceptually distinct from HDPG's measured effect of a
*human-specified deterministic risk constraint* layered
around a machine-generated ranking.

## Reviewer-response positioning (R2-08; overlaps R2-01/R1-06)

The updated Related Work section should:
1. Summarize the financial prediction baseline landscape.
2. Contrast selective abstention and familiar finance
   risk filters against human-defined governance.
3. Explicitly identify HDPG's tested treatment as a
   machine ranker + frozen deterministic P10 veto,
   **not** an experiment with real-time human intervention.
4. Explain economic-execution / turnover limitations
   and lack of current evidence across multiple rankers.

Bibliographic references are ready for manuscript
consideration but **not yet inserted into the source manuscript**.
They should be checked against the paper's existing
references to avoid duplication.
