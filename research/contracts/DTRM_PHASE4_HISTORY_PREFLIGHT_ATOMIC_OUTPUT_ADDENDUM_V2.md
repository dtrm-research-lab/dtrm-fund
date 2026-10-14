# Phase IV history preflight — atomic report publication addendum v2

**2026-10-14. REGISTERED BEFORE IMPLEMENTATION.** Applies only to the synthetic-only CLI in PR #35, following the original preregistration and review addendum v1. No amendment to frozen Phase III/MM1 or Stage-0 estimand.

## Trigger

Codex exact-head `4fedcc0` P2 review: exclusive `Path.open("xb")` can leave an empty or truncated **final-name** report after a write, flush or close error. Fail-closed CLI and evidence provenance require distinguishing a **fully written published** report from a failed, partially written one.

## Required behavior

1. Validate synthetic fixture and produce canonical bytes entirely in memory before any output file creation.
2. Stage bytes in a securely created, exclusively owned temporary file **in the target output directory**; flush and `fsync`, then close successfully.
3. Publish the complete file at the final output path using an **atomic no-clobber** operation supported by the target filesystem. Prefer `os.link(stage_path, final_path)` on the same filesystem, which fails if destination exists (regular file or symlink), over `os.replace`, which could overwrite external evidence. No fallback that overwrites a file.
4. Remove the temporary file in success and all error paths. On any stage write/fsync/close/link failure, the final report path must remain absent if initially absent. Any externally created destination is preserved. Errors are fixed/redacted.
5. Report bytes and scientific flags remain unchanged from review addendum v1; no real source or AWS calls.
6. Acceptance tests inject a staged write durability failure and a publish/link failure, assert **no final report and no orphan temporary file**. Existing no-overwrite, symlink and invalid-fixture checks must remain green; Python 3.10+ and macOS/Linux behavior must be reviewed.

The original source-authority gate remains `BLOCKED_SOURCE_AUDIT`; atomic synthetic output does not supply external provenance, history construction, permission to fit, or G5 closure.
