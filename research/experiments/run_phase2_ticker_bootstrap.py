from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_phase2_primary_bootstrap import (
    COHORTS,
    REPLICATES,
    TOPK_FRACTION,
    evaluate_selection,
    load_cohort,
    percentile_interval,
)


SEED = 20260822

OUTPUT_SUMMARY = Path(
    "research/local_data/probabilistic_phase2_ticker_bootstrap_summary.json"
)
OUTPUT_DISTRIBUTIONS = Path(
    "research/local_data/probabilistic_phase2_ticker_bootstrap_distributions.npz"
)


def ticker_cluster_bootstrap(
    df: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, int]:
    prediction = df["baseline_prediction"].to_numpy()
    p10_pass = df["p10_pass"].to_numpy(dtype=bool)
    target = df["target_model"].to_numpy()

    cluster_codes, cluster_labels = pd.factorize(
        df["ticker"],
        sort=False,
    )

    n_clusters = len(cluster_labels)
    row_index = np.arange(len(df))

    delta_mean = np.empty(REPLICATES, dtype=np.float64)
    delta_hit = np.empty(REPLICATES, dtype=np.float64)

    infeasible = 0

    for replicate in range(REPLICATES):
        draws = rng.integers(
            0,
            n_clusters,
            size=n_clusters,
        )

        counts = np.bincount(
            draws,
            minlength=n_clusters,
        )

        row_multiplicity = counts[cluster_codes]

        resampled_idx = np.repeat(
            row_index,
            row_multiplicity,
        )

        result = evaluate_selection(
            prediction[resampled_idx],
            p10_pass[resampled_idx],
            target[resampled_idx],
        )

        if result is None:
            infeasible += 1
            delta_mean[replicate] = np.nan
            delta_hit[replicate] = np.nan
        else:
            delta_mean[replicate] = result["delta_topk_mean"]
            delta_hit[replicate] = result["delta_topk_hit_rate"]

        if (replicate + 1) % 1000 == 0:
            print(
                f"  bootstrap {replicate + 1}/{REPLICATES}",
                flush=True,
            )

    return delta_mean, delta_hit, infeasible


def main() -> None:
    rng = np.random.default_rng(SEED)

    summary = {
        "method": "ticker_cluster_bootstrap",
        "replicates": REPLICATES,
        "seed": SEED,
        "confidence_level": 0.95,
        "interval": "percentile",
        "quantile_method": "linear",
        "topk_fraction": TOPK_FRACTION,
        "cohorts": {},
    }

    distributions = {}

    for cohort_name, config in COHORTS.items():
        print(f"\n{cohort_name}")

        df = load_cohort(
            config["signals"],
            config["targets"],
        )

        point = evaluate_selection(
            df["baseline_prediction"].to_numpy(),
            df["p10_pass"].to_numpy(dtype=bool),
            df["target_model"].to_numpy(),
        )

        if point is None:
            raise RuntimeError(
                f"{cohort_name}: frozen observed selection is infeasible"
            )

        if not np.isclose(
            point["delta_topk_mean"],
            config["expected_delta_mean"],
            rtol=0.0,
            atol=1e-12,
        ):
            raise RuntimeError(
                f"{cohort_name}: point delta mean does not reproduce"
            )

        if not np.isclose(
            point["delta_topk_hit_rate"],
            config["expected_delta_hit"],
            rtol=0.0,
            atol=1e-12,
        ):
            raise RuntimeError(
                f"{cohort_name}: point delta hit does not reproduce"
            )

        print("  rows:", len(df))
        print("  ticker clusters:", df["ticker"].nunique())
        print("  point delta mean:", point["delta_topk_mean"])
        print("  point delta hit:", point["delta_topk_hit_rate"])
        print("  point reproduction: PASS")

        delta_mean, delta_hit, infeasible = ticker_cluster_bootstrap(
            df,
            rng,
        )

        print("  infeasible replicates:", infeasible)

        if infeasible != 0:
            raise RuntimeError(
                f"{cohort_name}: {infeasible} bootstrap replicates "
                "could not fill Top-K"
            )

        summary["cohorts"][cohort_name] = {
            "rows": len(df),
            "ticker_clusters": int(df["ticker"].nunique()),
            "point_estimate": point,
            "bootstrap": {
                "infeasible_replicates": infeasible,
                "delta_topk_mean_ci95": percentile_interval(delta_mean),
                "delta_topk_hit_rate_ci95": percentile_interval(delta_hit),
            },
        }

        distributions[f"{cohort_name}_delta_topk_mean"] = delta_mean
        distributions[f"{cohort_name}_delta_topk_hit_rate"] = delta_hit

    OUTPUT_SUMMARY.write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    np.savez_compressed(
        OUTPUT_DISTRIBUTIONS,
        **distributions,
    )

    print("\nSaved:")
    print(OUTPUT_SUMMARY)
    print(OUTPUT_DISTRIBUTIONS)


if __name__ == "__main__":
    main()
