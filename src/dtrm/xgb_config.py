"""Legacy XGBoost configuration."""


def legacy_xgb_params() -> dict:
    """Return the exact trumpDataModel_v4 XGBoost parameters."""

    return {
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "max_depth": 4,
        "eta": 0.05,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 10,
        "alpha": 0.5,
        "lambda": 2.0,
        "tree_method": "hist",
        "max_bin": 128,
        "seed": 42,
        "nthread": 1,
        "verbosity": 1,
    }


LEGACY_NUM_BOOST_ROUND = 2000
LEGACY_EARLY_STOP_ROUNDS = 120
LEGACY_TOPK_FRAC = 0.10
LEGACY_TOPK_SCAN_STEP = 10