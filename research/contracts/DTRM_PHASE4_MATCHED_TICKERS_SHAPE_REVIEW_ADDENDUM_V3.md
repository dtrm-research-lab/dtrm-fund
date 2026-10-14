# Phase IV matched-tickers shape audit — review addendum v3: unbuffered advisory status

**2026-10-14 | REGISTERED BEFORE IMPLEMENTATION.** Applies only to PR #40 dormant operator CLI. Codex re-reviewed exact head `6889740492a845fec042ecd954147642da51fd40` and found one P2: a Python buffered `print` may return successfully but fail only at interpreter-shutdown flush after the report is published, replacing true success with exit 120 / unredacted BrokenPipeError. The previous synchronous failure guard is insufficient.

## Remediation

Replace the terminal status writer with a **single direct unbuffered OS stdout write** to file descriptor 1, using `os.write(1, exact_canonical_json_bytes + b"\\n")`; no `print` or Python buffered stdout object may own these bytes. Emit only the existing sanitized JSON status envelope and no source values, URI, credentials, paths or exception text. Catch `OSError` (including `BrokenPipeError`) directly at the status writer boundary; a console failure is best-effort and cannot mutate the separately published report or change a successful main exit code. No retry/backfill or invocation of provider/data operations.

Tests shall use file-descriptor capture (rather than object-only `capsys`) for successful/status error bytes; inject a synchronous direct-writer exception, and an **actual closed-pipe subprocess** that publishes a fake synthetic aggregate report, then ensure it returns exit 0 with the full report still present, no buffered flush exit 120 and no sensitive traceback. Failures before publication must continue returning error, and report output remains atomic fsynced no-clobber with best-effort post-publication stage cleanup. No production source access in tests.

All source/clock/mapping/fit/target/MM1 rights remain FALSE; actual operator-local Mongo invocation requires separate user approval. This is an engineering reliability correction, not scientific promotion.
