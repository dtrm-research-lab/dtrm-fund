# Phase IV — first current-Mongo observation and AWS handoff

This is a **source-only, read-only, non-atomic** pilot of the existing Mongo collection. It does NOT authenticate when a news story was first observed historically, modify MM1, trigger AWS or replace the existing 14-day v3 source-probe campaign.

## Local operator execution after PR review

From an existing private Mac checkout of dtrm-fund with previously working Mongo credentials:

```bash
git fetch origin
git switch --track origin/feature/phase4-mongo-observed-window-pilot-v0
OUT="$HOME/Phase4-private-archive-backup/phase4_current_window_$(date -u +%Y%m%dT%H%M%SZ).json"
PYTHONPATH=src python3 research/experiments/run_phase4_current_mongo_observed_window_v0.py \
  --output "$OUT"
shasum -a 256 "$OUT"
```

If the existing private Mongo configuration previously required --env-file, add that option with the **same operator-private path** before --output; never paste the path, .env contents or Mongo URI. If already on the feature branch, use git pull --ff-only instead of git switch --track. The output parent directory must already be private, owned by the user and not group/world writable.

The CLI reads only trumpMinMax.trumpNews with majority read concern, checks ≤250,000 documents, projects _id/date/text/matched_tickers sorted by _id, bounds every projected BSON document, performs initial/final count consistency checks and writes only aggregate UTC publication-day coverage counts, ticker-element **shape categories**, and the digest of the complete ordered projected-BSON stream to a new private 0600 file. **A count-consistent read is not a snapshot-isolation guarantee.** Mongo may be modified between reads; the result is only a current observation, not proof of original past source availability or a history suitable for fitting.

Share only the console status, aggregate counts and SHA-256, never raw source documents, ticker identities, article URLs or private JSON. No outcome access, fitting, first-seen assertion, AWS or MM1 execution is enabled.

## AWS next operational action

Backend tech-com-UA00001/theresistance-back PR #170 merged the **offline diagnostic-only** Lambda release. The operator previously produced a deterministic 39,086-byte ZIP with SHA256 ecb8180f00fad2d66351d3c7c2baf2fee5c9b20cb0d0fbb1209221d1f41d2971. This is NOT a verified S3 upload or an active Lambda.

1. Perform a fresh **read-only** AWS identity/bucket/Lambda inventory in eu-west-1 and verify real security/cost gates. The existing CloudFormation REVIEW_IN_PROGRESS preview cannot be treated as a deployed stack.
2. After separate review and explicit named approval, upload the exact *diagnostic ZIP* (no Mongo news) to an approved S3 versioned Object-Locked bucket with checksum, and independently verify VersionId before deploying the dormant diagnostic Lambda.
3. After another authorization, run one **noncounting** real EventBridge→Lambda→DynamoDB/GitHub diagnostic, with no provider calls or scientific slots.
4. Only after authenticated source-value-free diagnostic provenance and scientific v3 auditor readiness, freeze the future 14-day 56-slot campaign (≥48 eligible with both first and last days; no early PASS). A separate approved capture adapter must connect current Mongo snapshots to private scientific storage; the v3 source-probe alone does not make current Mongo snapshots immutable.

No writes to AWS, GitHub dispatch, Mongo, frozen Phase III or production are made by the current pilot.
