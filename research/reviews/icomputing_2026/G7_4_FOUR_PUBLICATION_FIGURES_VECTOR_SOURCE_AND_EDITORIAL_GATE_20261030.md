# G7.4 — Four IC figure source/format audit and independent vector release

Date 2026-10-30. Case ICOMPUTING-D-26-01069. **Author-held private artifacts NOT uploaded to this public GitHub repo.** Editorial file-source QA and graphics regeneration only; no new model test, no new old financial data, no raw event outcomes opened, no scientific score change.

## Source audit
Compared original submitted candidate `Beat_The_Machine_Intelligent_Computing_Submission_FINAL_v2.docx` against G7.1 draft `IC_G7_1_MANUSCRIPT_SCIENCE_FORMAT_AUDITED_WORKING_20261030.docx`. Their same four embedded raster figures were bitwise identical. Original standalone vector source or plot-generation provenance **not established** in bounded connected source search. Original embedded raster Figure 1 incorrectly claimed an 'Untouched temporal test' and Figure 2 said 'Prospective replication' for V3, inconsistent with now-confirmed 60-day outcome overlap.

**Action:** recreated four source-transparent figures from Python Matplotlib, not by rescaling or exporting embedded Word graphics. For each Figure 1–4 generated an editable SVG, vector PDF (no embedded raster images), and fresh 450dpi PNG. Figure 1–2 architecture/protocol labels revised to bounded G7.1 scientific claims. Figure 3 is replotted **strictly from G7.1 Table 3 published rounded points and CI endpoint values**, not original row-level data; Figure 4 is replotted from the manuscript's **4-decimal rounded V4 W18–W23** summary, not an authenticated historical graph-generation script. No claim of full native floating chart precision.

## Private outputs and immutable authorship handoff
- `IC_G7_4_FOUR_VECTOR_FIGURES_AND_SOURCES_20261030.zip` SHA256 **`5082e6e76437134b8a5813570b3a78a78e6921d3d0fdcc86d50dfcbb7e09037c`**. Contains four separate *PDF + SVG + 450dpi PNG*, source generator `build_figures_g74.py`, JSON provenance manifest with all source and figure SHA256, audit note and the original embedded PNGs in `archive_only_original_inset/` (archive evidence, **not** journal figures).
- Revised manuscript `IC_G7_4_FIGURES_ALIGNED_MANUSCRIPT_WORKING_20261030.docx` SHA256 **`712a84d376e566c47fb19538aeec59d8b57f0307f3ab0f702a1cb96d2f762e05`**. Four regenerated graphics integrated; only Fig. 3/4 captions adjusted for published rounded data. **All eight tables' text/cells identical to G7.1; all other manuscript paragraphs unchanged** (automated python-docx text assertions PASS). 22-page document rendered, visuals checked, no figure cutoffs. G7.1 had 21 pages: original G7.2 manuscript **page/line anchors are now stale**, and must be regenerated on final G7.5/G7.6 freeze.
- Audit note `G7_4_AUDITORIA_FIGURAS_20261030.md` (kept author-held, not public in GitHub).

## Actual publisher instructions
IC original editor asks four separate high-resolution editable figures at revision. Its author page permits vector PDF/EPS for diagrams and >=300 dpi raster, and prohibits submitted figures simply embedded in Word or created in Word/PowerPoint and converted. Source-native Python Matplotlib vector PDFs/SVG source and 450dpi bitmaps address the format requirement (format alone cannot certify original scientific data or third-party rights). **Use four standalone vector PDFs as main reviewer-upload candidates**, not embedded Word images, and author should supply/retain separately editable SVG sources.

## Open blockers
- **AUTHOR FIGURE-TRUTH SIGNOFF**: compare original source plotting code or exact figure numerical values if available before considering the regenerated figures original evidence; the reconstructed Fig3/4 from rounded manuscript statistics are faithful at publication precision but not original source replay.
- **RIGHTS**: verify all artwork belongs to the author or has permissions; no third-party reused material silently accepted.
- **G7.2 LINE RESYNC** on final 22-page or later manuscript after G7.5 changes.
- Check final PDF appearance in Editorial Manager and upload 4 individual PDFs; do not upload the internal audit ZIP as a figure.

Verdict: `G7_4_FOUR_INDEPENDENT_SOURCE_NATIVE_VECTOR_FIGURE_CANDIDATES_QA_PASS`. **NOT YET FINAL EDITORIAL GO** pending author truth/rights, final manuscript line refs and figure confirmation. G4.13 science-readiness internal estimate remains 66.65/100.
