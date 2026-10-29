# G5.7c — Source-code-only notebook producer-lineage inspection

Case ICOMPUTING-D-26-01069 · 2026-10-29. **Protocol frozen before code implementation.**
**Outcome access is NOT authorized. The G5.7b local outcome is NO direct .py producer in bounded scope** (original report SHA `b8d0d10eef98fe57a85cd1ddc65262aaa905d01f53c3733f397389a2cf73e308`).

## Why expand to notebooks?

G5.7b conclusively classified the only exact references to the three June labels within the 38 scoped .py files as `run_phase2_primary_bootstrap.py`, a consumer using `pd.read_pickle` plus unrelated bootstrap `np.savez_compressed`. It is scientifically invalid to interpret this as evidence that V2/V3/V4 targets were produced using the reconstructed V0 TRAIN means. GitHub current main-branch commit list has no entries through 2026-06-30; code was published/committed later, so current repo history cannot prove the June original producer lineage.

## Audit scope and privacy

Search only original Notebook `.ipynb` files within the owner-authorized `~/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks` tree. Code content may contain secrets. The scanner **never executes notebook cells, never imports/opens financial Pickles, never loads market labels or reads other files referenced by notebooks**. Source-code text is examined only transiently. Report **relative notebook paths, overall file SHA, counts, code-cell findings and static call categories**, never executable source snippets, notebook outputs, return values, secret keys or per-ticker observations.

Unlike an ordinary `json.load`, the scanner must **stream a notebook JSON token by token and skip non-code values, including output cell values**, without decoding or collecting their data. It necessarily reads raw notebook bytes to advance the parser; this is NOT equivalent to a claim that notebook files were never opened. The operator explicitly authorizes this narrow notebook-code inspection with `--authorize-notebook-code-inspection` and can decline.

Bound file count, file size, total bytes, cell count and source bytes; reject symlink roots, traversal, malformed JSON, non-string code sources and overlarge notebooks. Don't overwrite previous G5.7a/b reports.

## Source-level scientific classification

- `EXACT_TARGET_WRITER_CANDIDATE`: code cell contains an **exact June target filename** and a specific direct archive write call bound syntactically to that same filename; STILL NOT execution proof.
- `POSSIBLE_DYNAMIC_TARGET_WRITER`: code cells contain code-path builders or source variables for `target_model` with a pickle writer; exact archive basename may be constructed dynamically. This is a lead, not proof.
- `EXACT_TARGET_REFERENCE_ONLY`: code cell references the archived basename as input, code lacks a matching writer.
- `NO_CODE_PRODUCER_FOUND_IN_SCOPE`: no identified writer candidate; does not rule out other locations, historical notebooks, restored backups, untracked scripts or deleted sources.

Never elevate a static candidate to actual historical generation, prove exact TRAIN q01/q99 and ticker centering, certify source archival timestamp or authorize original V2/V3/V4 outcome access. Any future effect attribution demands source-compatible original label reconstruction/number parity and separate owner authorization.

## Decision ladder

1. PASS a source-only notebook code-cell scanner on deliberately hostile fixtures; preserve G5.7b SHA and known false-positive.
2. Owner run source-only G5.7c in separate pinned worktree after explicit inspection permission. Preserve report SHA.
3. If plausible producer: audit its input split, label preprocessing and save lineage against preserved historical source manifests **without target values**. If evidence insufficient, stop with `LABEL_TRANSFORM_COMPATIBILITY_NOT_ESTABLISHED`.
4. If no producer: document irreducible source gap and keep earlier transformed-label comparison only. Do not generate 'novelty' by speculative recomputation or label fitting on old outcomes.

No retrospective significance, real P&L, independent unused 60d holdout or alternate pre-frozen ranker is established by scanning notebooks. G4.12 scientific score remains 64 baseline (~67 provisional documentary).
