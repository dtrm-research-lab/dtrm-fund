"""Build the frozen realized-price snapshot for Phase-3 MM1 V6.

This is the first Stage-2 outcome-access step for the preregistered temporal
replication. It is permitted only after the tracked V6 ex-ante decision
manifest is committed and the latest nominal target date has reached the NYSE
close. The builder snapshots prices only; it does not construct target_model,
evaluate either frozen action, or rerun MM1.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"

MANIFEST_PATH = (
    REPO_ROOT
    / "research"
    / "contracts"
    / "DTRM_PHASE3_MM1_V6_DECISION_MANIFEST.json"
)
SIGNALS_PATH = LOCAL_DATA / "phase3_mm1_v6_signals_frozen.pkl"
PRICE_OUTPUT = LOCAL_DATA / "phase3_mm1_v6_price_snapshot.pkl"
SUMMARY_OUTPUT = LOCAL_DATA / "phase3_mm1_v6_price_snapshot_summary.json"

PRICE_START = pd.Timestamp("2026-06-26")
PRICE_END = pd.Timestamp("2026-09-04")
REQUIRED_LAST_MARKET_DATE = pd.Timestamp("2026-09-04")
TARGET_MATURITY_UTC = datetime(2026, 9, 4, 20, 0, 0, tzinfo=timezone.utc)
FMP_ENDPOINT = "https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}"

REQUIRED_SIGNAL_COLUMNS = (
    "news_id",
    "ticker",
    "date_dt",
    "baseline_point_score",
    "baseline_rank",
    "raw_p10",
    "calibrated_p10",
    "phase2_guardrail_pass",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_target_maturity(now_utc: datetime | None = None) -> None:
    """Block Stage-2 price access until the 2026-09-04 NYSE close."""

    observed = now_utc or datetime.now(timezone.utc)
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    observed = observed.astimezone(timezone.utc)
    if observed < TARGET_MATURITY_UTC:
        raise RuntimeError(
            "V6 realized-price access is forbidden before the 2026-09-04 "
            "NYSE close (20:00 UTC)"
        )


def require_manifest_committed() -> dict:
    """Require the local V6 decision manifest bytes to exist in current HEAD."""

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing V6 decision manifest: {MANIFEST_PATH}")

    relative = str(MANIFEST_PATH.relative_to(REPO_ROOT))
    try:
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"],
            cwd=REPO_ROOT,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "V6 decision manifest must be committed before realized price access"
        ) from exc

    local = MANIFEST_PATH.read_bytes()
    if committed != local:
        raise RuntimeError(
            "Local V6 decision manifest differs from the committed Git version"
        )

    manifest = json.loads(local)
    if manifest.get("artifact") != "DTRM_PHASE3_MM1_V6_DECISION_MANIFEST":
        raise RuntimeError("Unexpected V6 decision manifest artifact identity")
    if manifest.get("status") != "decision_frozen_pending_git_commit":
        raise RuntimeError("Unexpected V6 decision manifest status")

    cohort = manifest.get("cohort", {})
    if cohort.get("id") != "V6":
        raise RuntimeError("Decision manifest does not identify V6")
    if cohort.get("latest_nominal_target_date") != "2026-09-04":
        raise RuntimeError("V6 latest nominal target date changed")

    firewall = manifest.get("information_firewall", {})
    if firewall.get("V6_realized_outcomes_accessed") is not False:
        raise RuntimeError("V6 manifest does not certify a clean ex-ante firewall")
    if firewall.get("manifest_commit_required_before_realized_evaluation") is not True:
        raise RuntimeError("V6 manifest does not require commit before evaluation")

    return manifest


def load_frozen_signals(manifest: dict) -> pd.DataFrame:
    expected = manifest.get("frozen_signals", {})
    expected_path = str(SIGNALS_PATH.relative_to(REPO_ROOT))
    if expected.get("path") != expected_path:
        raise RuntimeError("V6 frozen-signal path differs from decision manifest")
    if not SIGNALS_PATH.exists():
        raise FileNotFoundError(f"Missing frozen V6 signals: {SIGNALS_PATH}")

    actual_sha = sha256_file(SIGNALS_PATH)
    if actual_sha != expected.get("sha256"):
        raise RuntimeError("V6 frozen-signal SHA-256 differs from decision manifest")

    signals = pd.read_pickle(SIGNALS_PATH)
    missing = set(REQUIRED_SIGNAL_COLUMNS) - set(signals.columns)
    if missing:
        raise RuntimeError(f"Frozen V6 signals missing columns: {sorted(missing)}")
    if len(signals) != int(manifest["cohort_structure"]["rows"]):
        raise RuntimeError("Frozen V6 signal row count differs from decision manifest")
    if signals.duplicated(["news_id", "ticker"]).any():
        raise RuntimeError("Frozen V6 signals contain duplicate (news_id, ticker) keys")

    return signals


def required_tickers_from_signals(signals: pd.DataFrame) -> tuple[str, ...]:
    tickers = {str(value) for value in signals["ticker"].tolist()}
    tickers.add("SPY")
    return tuple(sorted(tickers))


def _load_fmp_key() -> str:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError(
            "Price snapshot builder requires the optional builder dependencies"
        ) from exc

    load_dotenv()
    key = os.getenv("fmp_apikey") or os.getenv("FMP_API_KEY")
    if not key:
        raise RuntimeError("Missing fmp_apikey or FMP_API_KEY in the environment")
    return key


def fetch_ticker_prices(
    session,
    *,
    api_key: str,
    ticker: str,
    retries: int = 3,
) -> pd.DataFrame:
    """Fetch canonical date/close rows from the frozen FMP v3 endpoint."""

    url = FMP_ENDPOINT.format(ticker=ticker)
    params = {
        "from": PRICE_START.strftime("%Y-%m-%d"),
        "to": PRICE_END.strftime("%Y-%m-%d"),
        "apikey": api_key,
    }

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            historical = payload.get("historical", [])
            if not historical:
                raise RuntimeError(f"FMP returned no historical prices for {ticker}")

            frame = pd.DataFrame(historical)[["date", "close"]].copy()
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
            frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
            frame["ticker"] = ticker
            return frame[["ticker", "date", "close"]]
        except Exception as exc:  # network/API failure is retried, never hidden
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.6)

    raise RuntimeError(f"FMP price fetch failed for {ticker}: {last_error}")


def validate_price_snapshot(
    prices: pd.DataFrame,
    *,
    required_tickers: Iterable[str],
) -> pd.DataFrame:
    required = tuple(sorted(set(str(t) for t in required_tickers)))
    expected_columns = ["ticker", "date", "close"]
    if list(prices.columns) != expected_columns:
        raise ValueError("Price snapshot must contain exactly ticker,date,close columns")

    frame = prices.copy()
    frame["ticker"] = frame["ticker"].astype(str)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.tz_localize(None)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")

    if frame.empty:
        raise ValueError("Price snapshot must not be empty")
    if frame[["ticker", "date", "close"]].isna().any().any():
        raise ValueError("Price snapshot contains missing or invalid values")
    if not np.isfinite(frame["close"].to_numpy(dtype=np.float64)).all():
        raise ValueError("Price snapshot contains non-finite closes")
    if (frame["close"] <= 0).any():
        raise ValueError("Price snapshot contains non-positive closes")
    if frame.duplicated(["ticker", "date"]).any():
        raise ValueError("Price snapshot contains duplicate ticker/date rows")

    present = set(frame["ticker"].unique())
    missing = set(required) - present
    extra = present - set(required)
    if missing:
        raise ValueError(f"Price snapshot missing required tickers: {sorted(missing)}")
    if extra:
        raise ValueError(f"Price snapshot contains unexpected tickers: {sorted(extra)}")

    if (frame["date"] < PRICE_START).any() or (frame["date"] > PRICE_END).any():
        raise ValueError("Price snapshot contains rows outside the frozen fetch window")

    max_dates = frame.groupby("ticker", sort=False)["date"].max()
    stale = sorted(
        ticker
        for ticker in required
        if pd.Timestamp(max_dates.loc[ticker]) < REQUIRED_LAST_MARKET_DATE
    )
    if stale:
        raise ValueError(
            "Price snapshot does not reach the required V6 market date for: "
            + ", ".join(stale)
        )

    return frame.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)


def require_outputs_absent() -> None:
    existing = [path for path in (PRICE_OUTPUT, SUMMARY_OUTPUT) if path.exists()]
    if existing:
        raise RuntimeError(
            "V6 price snapshot builder refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def main() -> None:
    require_outputs_absent()
    require_target_maturity()
    manifest = require_manifest_committed()
    signals = load_frozen_signals(manifest)
    tickers = required_tickers_from_signals(signals)

    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            "Price snapshot builder requires requests; install the builder dependencies"
        ) from exc

    api_key = _load_fmp_key()
    session = requests.Session()
    try:
        frames = [
            fetch_ticker_prices(session, api_key=api_key, ticker=ticker)
            for ticker in tickers
        ]
    finally:
        session.close()

    prices = validate_price_snapshot(
        pd.concat(frames, ignore_index=True),
        required_tickers=tickers,
    )

    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    prices.to_pickle(PRICE_OUTPUT)
    price_sha = sha256_file(PRICE_OUTPUT)

    summary = {
        "stage": "DTRM_PHASE3_MM1_V6_REALIZED_PRICE_SNAPSHOT",
        "status": "built_after_committed_exante_decision_after_target_maturity_before_realized_comparison",
        "decision_manifest": {
            "path": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "sha256": sha256_file(MANIFEST_PATH),
        },
        "source": {
            "provider": "Financial Modeling Prep",
            "endpoint": "api/v3/historical-price-full/{ticker}",
            "api_key_recorded": False,
        },
        "maturity_gate": {
            "latest_nominal_target_date": "2026-09-04",
            "earliest_price_access_utc": TARGET_MATURITY_UTC.isoformat(),
            "required_last_market_date": REQUIRED_LAST_MARKET_DATE.strftime("%Y-%m-%d"),
        },
        "window": {
            "from": PRICE_START.strftime("%Y-%m-%d"),
            "to": PRICE_END.strftime("%Y-%m-%d"),
        },
        "required_tickers": len(tickers),
        "rows": int(len(prices)),
        "min_date": prices["date"].min().date().isoformat(),
        "max_date": prices["date"].max().date().isoformat(),
        "output": {
            "path": str(PRICE_OUTPUT.relative_to(REPO_ROOT)),
            "sha256": price_sha,
        },
        "realized_comparison_computed": False,
        "target_model_computed": False,
        "MM1_reoptimized": False,
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V6 REALIZED PRICE SNAPSHOT")
    print("committed ex-ante manifest: PASS")
    print("target maturity gate: PASS")
    print("required tickers:", len(tickers))
    print("price rows:", len(prices))
    print("date range:", prices["date"].min().date(), "->", prices["date"].max().date())
    print("snapshot:", PRICE_OUTPUT)
    print("sha256:", price_sha)
    print("realized comparison computed: False")
    print("NEXT REQUIRED ACTION: freeze and verify this snapshot before target evaluation.")


if __name__ == "__main__":
    main()
