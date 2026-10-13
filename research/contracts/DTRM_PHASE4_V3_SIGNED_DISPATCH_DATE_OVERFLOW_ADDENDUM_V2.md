# Phase IV v3 — entire-window date overflow fail-closed addendum v2

**Preregistered before implementation.** Codex exact-head P2 at `e1f2f01d54f3e8daf150b622cb6de21b98a053de` observed that `_target_at(start_utc_day=date.max, slot=55)` can raise a raw Python `OverflowError` when calculating the last day of the 14-day prospective campaign.

## Frozen correction

- Validate the **full 14-day geometry**, not only the requested slot: computing `start_utc_day + timedelta(days=13)` with its UTC schedule clocks must be representable before accepting any slot.
- Catch `OverflowError` or invalid calendar-combination `ValueError` and emit fixed `SyntheticV3EnvelopeError("INVALID_TARGET")`. No Python raw error, secret, input value, or provider data is leaked.
- Add synthetic test cases near the date upper bound (e.g. `date.max` slot 0 and slot 55) to demand `INVALID_TARGET` even if the chosen first slot's instant fits. Also include the exactly representable maximum start day (Dec 18, 9999) as a tested boundary for the target geometry **without pretending a real campaign can start then**.
- No change to 14×4 slot clocks, 48/56 adequacy rules, HMAC, source contract, other permission flags, AWS, MM1, or Phase III.
- Rerun four exact-head CI workflows and Codex after implementation; do not merge or activate without separate authority.

This is an outcome-blind type/clock robustness correction to the **synthetic** signed-dispatch boundary.
