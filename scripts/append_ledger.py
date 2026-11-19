#!/usr/bin/env python3
"""
OCEI™ v2.2 Immutable Hourly Time-Series Ledger Logger
Fetches the live signed OCEI state from https://orbitcompute.ai/v1/index/ocei,
captures live European wholesale spot electricity (EPEX DE-LU),
and appends a SHA-256 hash-chained record into ledger/YYYY-MM.jsonl and ledger/latest.json.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys
import urllib.request
from typing import Any

OCEI_INDEX_URL = "https://orbitcompute.ai/v1/index/ocei"
OCEI_JWKS_URL = "https://orbitcompute.ai/.well-known/jwks.json"
EU_SPOT_URL = "https://api.energy-charts.info/price?bzn=DE-LU"
LEDGER_DIR = pathlib.Path("ledger")
LATEST_PATH = LEDGER_DIR / "latest.json"
GENESIS_HASH = "GENESIS_OCEI_V2_2_DOI_10_5281_ZENODO_24181722"
EUR_TO_USD_REF = 1.08


def fetch_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "OCEI-Ledger-Bot/1.1 (+https://github.com/Mr-Didi/mcp-ocei-oracle)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def fetch_live_eu_spot_price(breakeven_usd_mwh: float | None) -> dict[str, Any] | None:
    try:
        data = fetch_json(EU_SPOT_URL, timeout=12)
        timestamps = data.get("unix_seconds") or []
        prices = data.get("price") or []
        if not timestamps or not prices:
            return None
        now_ts = int(dt.datetime.now(dt.timezone.utc).timestamp())
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
        eur_mwh = round(float(prices[best_idx]), 2)
        usd_est = round(eur_mwh * EUR_TO_USD_REF, 2)
        ratio = round(usd_est / breakeven_usd_mwh, 2) if breakeven_usd_mwh else None
        return {
            "market": "EPEX_SPOT_DE_LU",
            "source": "energy-charts.info",
            "slot_utc": dt.datetime.fromtimestamp(timestamps[best_idx], tz=dt.timezone.utc).isoformat(),
            "price_eur_mwh": eur_mwh,
            "price_usd_mwh_est": usd_est,
            "multiple_vs_orbital_breakeven": ratio,
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
    std = ocei_payload.get("ocei_standard") or {}
    multi = std.get("multi_regime_comparison") or {}
    sw = ocei_payload.get("space_weather_and_young_daly_checkpointing") or {}
    att = ocei_payload.get("attestation") or {}

    jwks_kid = att.get("key_id")
    if not jwks_kid:
        try:
            jwks = fetch_json(OCEI_JWKS_URL, timeout=10)
            keys = jwks.get("keys") or []
            if keys and isinstance(keys[0], dict):
                jwks_kid = keys[0].get("kid")
        except Exception:
            pass

    ocei_spot = std.get("ocei_spot_realtime_score")
    ocei_structural = std.get("ocei_structural_5yr_score")
    ocei_twap = std.get("ocei_twap_60m_settlement_score")
    vleo_score = (multi.get("vleo_320km_self_cleaning_edge") or {}).get("score")
    spread_bps = std.get("net_orbital_spread_bps")
    breakeven_usd_mwh = std.get("breakeven_grid_usd_mwh")
    dispatch_signal = std.get("arbitrage_dispatch_signal")
    dispatch_directive = std.get("dispatch_directive")

    eu_spot = fetch_live_eu_spot_price(breakeven_usd_mwh)
    prev_hash, prev_seq, rolling_window = load_previous_head()

    if isinstance(ocei_spot, (int, float)):
        rolling_window = (rolling_window + [round(float(ocei_spot), 4)])[-24:]

    raw_payload_sha256 = sha256_hex(canonical_json(ocei_payload))

    summary = {
        "ocei_spot": ocei_spot,
        "ocei_structural": ocei_structural,
        "ocei_twap_60m": ocei_twap,
        "vleo_320km_score": vleo_score,
        "terrestrial_tier4_score": std.get("terrestrial_tier4_grid_score"),
        "net_orbital_spread_bps": spread_bps,
        "breakeven_grid_usd_mwh": breakeven_usd_mwh,
        "dispatch_signal": dispatch_signal,
        "dispatch_directive": dispatch_directive,
        "confidence_score": std.get("confidence_score"),
        "rolling_24h_mean_spot": round(sum(rolling_window) / len(rolling_window), 4)
        if rolling_window
        else None,
        "space_weather": {
            "status": sw.get("telemetry_status"),
            "observation_utc": sw.get("observation_utc"),
            "l1_lead_min": sw.get("l1_shockwave_lead_time_min"),
            "pre_emptive_trigger": sw.get("pre_emptive_checkpoint_trigger"),
            "f10_7_sfu": sw.get("solar_flux_f10_7_sfu"),
            "kp": sw.get("geomagnetic_kp_index"),
            "goes_proton_pfu": sw.get("goes_proton_flux_ge10mev_pfu"),
            "goes_xray_class": sw.get("goes_xray_flare_class"),
            "net_availability_pct": sw.get("net_effective_compute_availability_pct"),
        },
        "live_terrestrial_spot": eu_spot,
    }

    entry_body = {
        "schema": "ocei.ledger.v1",
        "sequence": prev_seq + 1,
        "recorded_utc": now.isoformat().replace("+00:00", "Z"),
        "source_endpoint": OCEI_INDEX_URL,
        "jwks_kid": jwks_kid,
        "oracle_state_hash_sha256": att.get("state_hash_sha256"),
        "prev_ledger_hash": prev_hash,
        "raw_payload_sha256": raw_payload_sha256,
        "summary": summary,
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
        "oracle_state_hash_sha256": att.get("state_hash_sha256"),
        "raw_payload_sha256": raw_payload_sha256,
        "jwks_kid": jwks_kid,
        "summary": summary,
        "rolling_24h_spot_window": rolling_window,
    }
    LATEST_PATH.write_text(json.dumps(latest_head, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"[OCEI LEDGER] seq={entry['sequence']} hash={ledger_entry_hash[:16]}... "
        f"spot={ocei_spot} twap={ocei_twap} signal={dispatch_signal} "
        f"avail={sw.get('net_effective_compute_availability_pct')}% eu_spot={eu_spot}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
