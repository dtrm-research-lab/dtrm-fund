# G7.5 — AI-assisted manuscript disclosure and reproducibility boundary gate

Date 2026-10-30 | Ms. No. ICOMPUTING-D-26-01069 | **Author-held editorial draft; not submission-authorized.**

## Publisher's explicit requirement

Official Intelligent Computing ethics: https://spj.science.org/page/icomputing/publication-ethics
- AI-assisted research, code, visualization and writing must be acknowledged in the cover letter and manuscript Acknowledgments.
- Methods must identify AI tool, version and **full prompts used in production**.
- AI cannot be an author; researcher retains accountability.
- Data/code needed to evaluate work must be accessible or restrictions and licensing limitations fully disclosed.

**No inference that a missing prompt/version is recovered merely because a model label or vendor name is known.**

## Private author-held outputs (NOT committed into public repo)

- Updated 22-page manuscript `IC_G7_5_AI_METHODS_REPRODUCIBILITY_DISCLOSED_WORKING_20261030.docx` SHA256 `27b8bc9aeda661ce12c1be8e129f8fae5dd51dbf6beece08ef328007ffd649d8`. Three paragraphs added under Methods Research governance (frozen software, human/AI roles, incomplete prompt provenance, data-vintage limits). Acknowledgments and Data Availability updated. Numerical 8-table XML cell content and all 4 existing figure binary SHA exactly identical to G7.4. Original abstract and results unchanged. 0 automated a11y issues.
- Separate 3-page private `IC_G7_5_AI_PROMPT_AND_REPRODUCIBILITY_INVENTORY_WORKING_20261030.docx` SHA256 `33fd185942347c29f53089dcadbe8589de3ed3275ab686972c4a881faabf2918`. A proper evidentiary matrix, NOT an invented retrospective prompt transcript. Table headers marked a11y; 0 findings.
- Single-page private `IC_G7_5_EDITOR_AI_USE_DISCLOSURE_COVER_WORKING_20261030.docx` SHA256 `eda8942052bfb142c07799205075ecc113ecf183b8246c5bb2f2b39124fb4510`. Does not claim complete disclosure.
- Private Spanish audit `G7_5_AUDITORIA_TRANSPARENCIA_REPRODUCIBILIDAD_20261030.md` SHA256 `175c1938a8004c64cd01b3fa5222fa9b0959c25d21059c2318cfd7b7f4c8d53c`.

## Evidence from immutable original public snapshot

- Commit `b20848fd8152f12f7dda2e4b015a3e527f46aa72`: `REPRODUCIBILITY.md`, `pyproject.toml`, configs/contracts, scripts and summaries all exist.
- The original guide specifies Python >=3.10, numpy/pandas, XGBoost 3.0.2, 390 input features (384 text embedding dimensions + five text statistics + beta_pre), quantile models, original Top-K rank iteration/threshold, and news_id/ticker 10,000 replicate bootstraps. No fully locked historical environment or original licensed dataset is in the public snapshot.
- Original guide labels V3 as *prospective replication* and suggests full reconstruction from equivalent vendor sources, which is now explicitly limited in G7.5: 60d windows overlap and archived June V2–V4 target producer/clip-center vintage remains unproven. **Do not modify immutable commit, but publish addendum warning instead.**
- V2–V4 differ on saved transformed `target_model` rather than raw tradable returns. No original market price acquisition-time integrity; no complete event-level buy/sell P&L; no independent unused 60-day holdout.
- G7.4 vector figures drawn from Matplotlib, not generative-image synthesis. Figures 3/4 reprised from rounded manuscript statistics, NOT original plot trace.

## AI inventory status

- OpenAI ChatGPT role in manuscript/revision is **documented**.
- For this **2026-10-30 G7.5 editing session only**, the active assistant identifies as GPT-6. This DOES NOT establish the LLM version used in earlier Phase II model-building, August submission or previous revision sessions. The exact per-call vendor builds, settings and full prompt texts of those sessions are not independently recovered.
- Few user-provided messages exist verbatim in this working project such as `dale con G7.4` and `g7 5`; those are task initiators, **NOT the complete AI prompt inventory** needed by the publisher. Never fabricate original prompt texts. Full history export and author validation remain required; if irrecoverable, request editorial-office guidance.
- Non-LLM XGBoost prediction/quantile algorithms are distinct from ChatGPT research-writing assistance.

## G7.5 outcome and strict release gates

**`G7_5_METHODS_CAVEATS_AND_DECLARATION_DRAFT_QA_PASS`**.
**`G7_5_FULL_VERBATIM_AI_PROMPT_AND_HISTORIC_VERSION_DISCLOSURE_OPEN`**.
**`G7_5_FINAL_SUBMISSION_NO_GO`** until author exports/verifies prompt sources or resolves missing records transparently with publisher, confirms historical versions/licenses and methods, and a frozen final G7.2 refreshes all final line numbers after G7.4/G7.5 editorial modifications.

Original G4.13 66.65/100 author-side science readiness is **unchanged**; editorial disclosures do not constitute new evidence.
