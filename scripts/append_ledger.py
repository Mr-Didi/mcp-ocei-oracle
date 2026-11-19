#!/usr/bin/env python3
"""
OCEI™ v2.2 Immutable Hourly Time-Series Ledger Logger
Fetches the live signed OCEI state from https://orbitcompute.ai/v1/index/ocei,
optionally captures live terrestrial EU wholesale spot electricity (EPEX DE-LU),
and appends a SHA-256 hash-chained record into ledger/YYYY-MM.jsonl and ledger/latest.json.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.request
from typing import Any

OCEI_INDEX_URL = "https://orbitcompute.ai/v1/index/ocei"
OCEI_JWKS_URL = "https://orbitcompute.ai/.well-known/jwks.json"
EU_SPOT_URL = "https://api.energy-charts.info/price?bzn=DE-LU"
LEDGER_DIR = pathlib.Path("ledger")
LATEST_PATH = LEDGER_DIR / "latest.json"
GENESIS_HASH = "GENESIS_OCEI_V2_2_DOI_10_5281_ZENODO_24181722"


def fetch_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "OCEI-Ledger-Bot/1.0 (+https://github.com/Mr-Didi/mcp-ocei-oracle)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization (RFC-8785 compatible for strings/ints/structs)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def extract_metric(payload: dict[str, Any], candidates: list[list[str]]) -> Any:
    """Schema-resilient lookup across flat or nested OCEI JSON structures."""
    for path in candidates:
        cur: Any = payload
        found = True
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                found = False
                break
        if found and cur is not None:
            return cur
    return None


def fetch_live_eu_spot_price() -> dict[str, Any] | None:
    """Non-blocking fetch of current EPEX Spot DE-LU electricity price (EUR/MWh)."""
    try:
        data = fetch_json(EU_SPOT_URL, timeout=12)
        timestamps = data.get("unix_seconds") or []
        prices = data.get("price") or []
        if not timestamps or not prices:
            return None
        now_ts = int(dt.datetime.now(dt.timezone.utc).timestamp())
        # Pick the latest slot <= now, or fallback to last non-null entry
        best_idx = None
        for idx, ts in enumerate(timestamps):
            if prices[idx] is not None and ts <= now_ts:
                best_idx = idx
        if best_idx is None:
            for idx in range(len(prices) - 1, -1, -1):
                if prices[idx] is not None:
                    best_idx = idx
                    break
        if best_idx is None:
            return None
        return {
            "market": "EPEX_SPOT_DE_LU",
            "source": "energy-charts.info",
            "slot_utc": dt.datetime.fromtimestamp(timestamps[best_idx], tz=dt.timezone.utc).isoformat(),
            "price_eur_mwh": round(float(prices[best_idx]), 2),
        }
    except Exception as exc:
        return {"market": "EPEX_SPOT_DE_LU", "status": "unavailable", "error": str(exc)}


def load_previous_head() -> tuple[str, int, list[float]]:
    if not LATEST_PATH.exists():
        return GENESIS_HASH, 0, []
    try:
        prev = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
        return (
            str(prev.get("ledger_entry_hash", GENESIS_HASH)),
            int(prev.get("sequence", 0)),
            list(prev.get("rolling_24h_spot_window", [])),
        )
    except Exception:
        return GENESIS_HASH, 0, []


def main() -> int:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    month_file = LEDGER_DIR / f"{now.strftime('%Y-%m')}.jsonl"

    ocei_payload = fetch_json(OCEI_INDEX_URL)
    jwks_kid = None
    try:
        jwks = fetch_json(OCEI_JWKS_URL, timeout=10)
        keys = jwks.get("keys") or []
        if keys and isinstance(keys[0], dict):
            jwks_kid = keys[0].get("kid")
    except Exception:
        pass

    eu_spot = fetch_live_eu_spot_price()
    prev_hash, prev_seq, rolling_window = load_previous_head()

    ocei_spot = extract_metric(
        ocei_payload,
        [
            ["ocei_spot"],
            ["index", "ocei_spot"],
            ["scores", "spot"],
            ["ocei", "spot"],
            ["score"],
        ],
    )
    ocei_structural = extract_metric(
        ocei_payload,
        [
            ["ocei_structural"],
            ["index", "ocei_structural"],
            ["scores", "structural"],
            ["ocei", "structural"],
        ],
    )
    ocei_twap = extract_metric(
        ocei_payload,
        [
            ["ocei_twap_60m"],
            ["index", "ocei_twap_60m"],
            ["scores", "twap_60m"],
            ["twap_60m"],
        ],
    )
    dispatch_signal = extract_metric(
        ocei_payload,
        [
            ["dispatch_signal"],
            ["signal"],
            ["arbitrage", "dispatch_signal"],
            ["routing", "dispatch_signal"],
            ["decision"],
        ],
    )

    if isinstance(ocei_spot, (int, float)):
        rolling_window = (rolling_window + [round(float(ocei_spot), 4)])[-24:]

    raw_payload_sha256 = sha256_hex(canonical_json(ocei_payload))

    entry_body = {
        "schema": "ocei.ledger.v1",
        "sequence": prev_seq + 1,
        "recorded_utc": now.isoformat().replace("+00:00", "Z"),
        "source_endpoint": OCEI_INDEX_URL,
        "jwks_kid": jwks_kid,
        "prev_ledger_hash": prev_hash,
        "raw_payload_sha256": raw_payload_sha256,
        "summary": {
            "ocei_spot": ocei_spot,
            "ocei_structural": ocei_structural,
            "ocei_twap_60m": ocei_twap,
            "dispatch_signal": dispatch_signal,
            "rolling_24h_mean_spot": round(sum(rolling_window) / len(rolling_window), 4)
            if rolling_window
            else None,
            "live_terrestrial_spot": eu_spot,
        },
        "signed_payload": ocei_payload,
    }

    ledger_entry_hash = sha256_hex(canonical_json(entry_body))
    entry = {**entry_body, "ledger_entry_hash": ledger_entry_hash}

    with month_file.open("a", encoding="utf-8") as fh:
        fh.write(canonical_json(entry) + "\n")

    latest_head = {
        "schema": "ocei.ledger.head.v1",
        "sequence": entry["sequence"],
        "recorded_utc": entry["recorded_utc"],
        "ledger_file": str(month_file).replace("\\", "/"),
        "prev_ledger_hash": prev_hash,
        "ledger_entry_hash": ledger_entry_hash,
        "raw_payload_sha256": raw_payload_sha256,
        "jwks_kid": jwks_kid,
        "summary": entry["summary"],
        "rolling_24h_spot_window": rolling_window,
    }
    LATEST_PATH.write_text(json.dumps(latest_head, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"[OCEI LEDGER] seq={entry['sequence']} hash={ledger_entry_hash[:16]}... "
        f"spot={ocei_spot} signal={dispatch_signal} eu_spot={eu_spot}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
