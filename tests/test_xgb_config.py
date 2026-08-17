from dtrm.xgb_config import (
    LEGACY_EARLY_STOP_ROUNDS,
    LEGACY_NUM_BOOST_ROUND,
    LEGACY_TOPK_FRAC,
    LEGACY_TOPK_SCAN_STEP,
    legacy_xgb_params,
    quantile_xgb_params,
)


def test_legacy_xgb_params():
    params = legacy_xgb_params()

    assert params == {
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

def test_quantile_xgb_params_preserve_baseline_structure():
    baseline = legacy_xgb_params()

    for alpha in (0.1, 0.5, 0.9):
        params = quantile_xgb_params(alpha)

        assert params["objective"] == "reg:quantileerror"
        assert params["quantile_alpha"] == alpha
        assert "eval_metric" not in params

        for key, value in baseline.items():
            if key in {"objective", "eval_metric"}:
                continue

            assert params[key] == value

assert LEGACY_NUM_BOOST_ROUND == 2000
assert LEGACY_EARLY_STOP_ROUNDS == 120
assert LEGACY_TOPK_FRAC == 0.10
assert LEGACY_TOPK_SCAN_STEP == 10