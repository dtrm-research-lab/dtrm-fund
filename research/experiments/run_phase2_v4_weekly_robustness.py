from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_phase2_primary_bootstrap import (
    COHORTS,
    TOPK_FRACTION,
    evaluate_selection,
    load_cohort,
)


OUTPUT = Path(
    "research/local_data/"
    "probabilistic_phase2_v4_weekly_robustness_summary.json"
)


def main() -> None:
    config = COHORTS["V4"]

    df = load_cohort(
        config["signals"],
        config["targets"],
    ).copy()

    # Gate: reproduce the frozen full-cohort V4 result before
    # computing any temporal partition.
    full = evaluate_selection(
        df["baseline_prediction"].to_numpy(),
        df["p10_pass"].to_numpy(dtype=bool),
        df["target_model"].to_numpy(),
    )

    if full is None:
        raise RuntimeError("V4 full-cohort frozen selection is infeasible")

    if not np.isclose(
        full["delta_topk_mean"],
        config["expected_delta_mean"],
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("V4 full-cohort delta mean does not reproduce")

    if not np.isclose(
        full["delta_topk_hit_rate"],
        config["expected_delta_hit"],
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("V4 full-cohort delta hit does not reproduce")

    dates = pd.to_datetime(
        df["date_dt_signal"],
        utc=True,
    )

    iso = dates.dt.isocalendar()

    df["iso_year"] = iso["year"].to_numpy()
    df["iso_week"] = iso["week"].to_numpy()

    weekly_results = []

    grouped = df.groupby(
        ["iso_year", "iso_week"],
        sort=True,
        observed=True,
    )

    for (year, week), w in grouped:
        result = evaluate_selection(
            w["baseline_prediction"].to_numpy(),
            w["p10_pass"].to_numpy(dtype=bool),
            w["target_model"].to_numpy(),
        )

        if result is None:
            raise RuntimeError(
                f"ISO week {int(year)}-W{int(week):02d} "
                "cannot fill candidate Top-K"
            )

        weekly_results.append(
            {
                "iso_year": int(year),
                "iso_week": int(week),
                "label": f"{int(year)}-W{int(week):02d}",
                "start_date": str(dates.loc[w.index].min().date()),
                "end_date": str(dates.loc[w.index].max().date()),
                "rows": int(result["rows"]),
                "topk_rows": int(result["topk_rows"]),
                "baseline_topk_mean": result["baseline_topk_mean"],
                "candidate_topk_mean": result["candidate_topk_mean"],
                "delta_topk_mean": result["delta_topk_mean"],
                "baseline_topk_hit_rate": result[
                    "baseline_topk_hit_rate"
                ],
                "candidate_topk_hit_rate": result[
                    "candidate_topk_hit_rate"
                ],
                "delta_topk_hit_rate": result[
                    "delta_topk_hit_rate"
                ],
            }
        )

    if not weekly_results:
        raise RuntimeError("No ISO weeks produced")

    delta_means = np.array(
        [x["delta_topk_mean"] for x in weekly_results],
        dtype=np.float64,
    )

    positive_weeks = int((delta_means > 0).sum())
    total_weeks = len(weekly_results)

    summary = {
        "method": "ISO_8601_calendar_week_partition",
        "cohort": "V4",
        "topk_fraction": TOPK_FRACTION,
        "include_partial_boundary_weeks": True,
        "full_cohort_reproduction": full,
        "weeks": weekly_results,
        "temporal_summary": {
            "total_weeks": total_weeks,
            "positive_delta_topk_mean_weeks": positive_weeks,
            "fraction_of_weeks_with_positive_delta_topk_mean": (
                positive_weeks / total_weeks
            ),
        },
        "interpretation": "descriptive",
    }

    OUTPUT.write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    print("full cohort reproduction: PASS")
    print("weeks:", total_weeks)
    print("saved:", OUTPUT)


if __name__ == "__main__":
    main()
