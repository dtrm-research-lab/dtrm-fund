# Phase IV B mechanics — bounded lookback arithmetic addendum v1

**2026-10-14, registered before code correction.** This narrowly completes the synthetic lookback validation contract for PR #39.

The cutoff may be an otherwise syntactically legal UTC instant at the extreme of Python's representable datetime range. Subtracting even the minimum positive lookback can underflow. Such synthetic combinations **must fail closed** with the same fixed `INVALID_PHASE4_SYNTHETIC_HISTORY` domain error, never raise an uncontrolled `OverflowError`, choose a different history boundary, or clamp timestamps.

Unit test: `decision_cutoff=0001-01-01T00:00:00Z`, `lookback_days=2` fails without scientific promotion. Canonical window remains `[cutoff - L days, cutoff)`, all source/maturity/ML/MM1 flags remain false. No live access, AWS or scientific fitting authorized.
