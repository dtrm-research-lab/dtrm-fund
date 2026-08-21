from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


REPLICATES = 10_000
SEED = 20260821
TOPK_FRACTION = 0.10

OUTPUT_SUMMARY = Path(
    "research/local_data/probabilistic_phase2_primary_bootstrap_summary.json"
)
OUTPUT_DISTRIBUTIONS = Path(
    "research/local_data/probabilistic_phase2_primary_bootstrap_distributions.npz"
)

COHORTS = {
    "V2": {
        "signals": Path(
            "research/local_data/"
            "probabilistic_v2_holdout_signals_2026-06-10.pkl"
        ),
        "targets": Path(
            "research/local_data/"
            "probabilistic_v2_holdout_model_targets_2026-06-10.pkl"
        ),
        "expected_delta_mean": 0.14429480582475662,
        "expected_delta_hit": 0.5788288288288288,
    },
    "V3": {
        "signals": Path(
            "research/local_data/"
            "probabilistic_v3_holdout_signals_2026-06-14.pkl"
        ),
        "targets": Path(
            "research/local_data/"
            "probabilistic_v3_holdout_model_targets_2026-06-14.pkl"
        ),
        "expected_delta_mean": 0.14943748898804188,
        "expected_delta_hit": 0.5851063829787234,
    },
    "V4": {
        "signals": Path(
            "research/local_data/"
            "probabilistic_v4_holdout_signals_2026-06-06.pkl"
        ),
        "targets": Path(
            "research/local_data/"
            "probabilistic_v1_holdout_model_targets_2026-06-06.pkl"
        ),
        "expected_delta_mean": 0.027561593800783157,
        "expected_delta_hit": 0.10168650793650791,
    },
}


def load_cohort(signals_path: Path, targets_path: Path) -> pd.DataFrame:
    signals = pd.read_pickle(signals_path)
    targets = pd.read_pickle(targets_path)

    required_signals = {
        "news_id",
        "ticker",
        "date_dt",
        "baseline_prediction",
        "p10_pass",
    }
    required_targets = {
        "news_id",
        "ticker",
        "date_dt",
        "target_model",
    }

    if not required_signals.issubset(signals.columns):
        missing = required_signals - set(signals.columns)
        raise ValueError(f"Missing signal columns: {sorted(missing)}")

    if not required_targets.issubset(targets.columns):
        missing = required_targets - set(targets.columns)
        raise ValueError(f"Missing target columns: {sorted(missing)}")

    if signals.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicate signal keys")

    if targets.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicate target keys")

    df = signals.merge(
        targets[["news_id", "ticker", "date_dt", "target_model"]],
        on=["news_id", "ticker"],
        how="inner",
        validate="one_to_one",
        sort=False,
        suffixes=("_signal", "_target"),
    )

    if len(df) != len(signals) or len(df) != len(targets):
        raise ValueError("Signal/target merge is not complete")

    signal_dates = pd.to_datetime(df["date_dt_signal"])
    target_dates = pd.to_datetime(df["date_dt_target"])

    if not signal_dates.equals(target_dates):
        raise ValueError("Signal and target dates differ")

    if not np.isfinite(df["baseline_prediction"].to_numpy()).all():
        raise ValueError("Non-finite baseline predictions")

    if not np.isfinite(df["target_model"].to_numpy()).all():
        raise ValueError("Non-finite model targets")

    return df


def evaluate_selection(
    prediction: np.ndarray,
    p10_pass: np.ndarray,
    target: np.ndarray,
) -> dict[str, float | int] | None:
    n = len(target)
    k = int(n * TOPK_FRACTION)

    if k <= 0:
        raise ValueError("Top-K is empty")

    # Exact frozen ranking convention used by the baseline evaluator.
    order = np.argsort(-prediction)

    baseline_idx = order[:k]

    passing_order = order[p10_pass[order]]
    if len(passing_order) < k:
        return None

    candidate_idx = passing_order[:k]

    baseline_mean = float(target[baseline_idx].mean())
    candidate_mean = float(target[candidate_idx].mean())

    baseline_hit = float((target[baseline_idx] > 0).mean())
    candidate_hit = float((target[candidate_idx] > 0).mean())

    return {
        "rows": n,
        "topk_rows": k,
        "baseline_topk_mean": baseline_mean,
        "candidate_topk_mean": candidate_mean,
        "delta_topk_mean": candidate_mean - baseline_mean,
        "baseline_topk_hit_rate": baseline_hit,
        "candidate_topk_hit_rate": candidate_hit,
        "delta_topk_hit_rate": candidate_hit - baseline_hit,
    }


def cluster_bootstrap(
    df: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, int]:
    prediction = df["baseline_prediction"].to_numpy()
    p10_pass = df["p10_pass"].to_numpy(dtype=bool)
    target = df["target_model"].to_numpy()

    cluster_codes, cluster_labels = pd.factorize(
        df["news_id"],
        sort=False,
    )

    n_clusters = len(cluster_labels)
    row_index = np.arange(len(df))

    delta_mean = np.empty(REPLICATES, dtype=np.float64)
    delta_hit = np.empty(REPLICATES, dtype=np.float64)

    infeasible = 0

    for replicate in range(REPLICATES):
        # Uniform cluster draws with replacement.
        draws = rng.integers(
            0,
            n_clusters,
            size=n_clusters,
        )

        # Each repeated cluster draw duplicates all rows belonging
        # to that cluster.
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


def percentile_interval(values: np.ndarray) -> list[float]:
    return [
        float(np.quantile(values, 0.025, method="linear")),
        float(np.quantile(values, 0.975, method="linear")),
    ]


def main() -> None:
    # One deterministic generator for the frozen sequence
    # V2 -> V3 -> V4.
    rng = np.random.default_rng(SEED)

    summary = {
        "method": "news_id_cluster_bootstrap",
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

        # Gate: reproduce the already-known frozen result before
        # any inferential computation.
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
        print("  news_id clusters:", df["news_id"].nunique())
        print("  point delta mean:", point["delta_topk_mean"])
        print("  point delta hit:", point["delta_topk_hit_rate"])
        print("  point reproduction: PASS")

        delta_mean, delta_hit, infeasible = cluster_bootstrap(
            df,
            rng,
        )

        print("  infeasible replicates:", infeasible)

        # Contract requires every bootstrap replicate to fill Top-K.
        if infeasible != 0:
            raise RuntimeError(
                f"{cohort_name}: {infeasible} bootstrap replicates "
                "could not fill Top-K"
            )

        mean_ci = percentile_interval(delta_mean)
        hit_ci = percentile_interval(delta_hit)

        summary["cohorts"][cohort_name] = {
            "rows": len(df),
            "news_id_clusters": int(df["news_id"].nunique()),
            "point_estimate": point,
            "bootstrap": {
                "infeasible_replicates": infeasible,
                "delta_topk_mean_ci95": mean_ci,
                "delta_topk_hit_rate_ci95": hit_ci,
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
