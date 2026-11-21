#!/usr/bin/env python3
"""
OCEI v2.3 Hourly Cryptographic Ledger Appender (Zero External Dependencies).
Fetches RFC-8785 / ES256-attested live state from orbitcompute.ai/v1/index/ocei,
continues the immutable SHA-256 hash chain in ledger/YYYY-MM.jsonl, and updates ledger/latest.json.
"""
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone

ORACLE_URL = "https://orbitcompute.ai/v1/index/ocei"
GENESIS_HASH = "GENESIS_OCEI_V2_2_DOI_10_5281_ZENODO_24181722"
LEDGER_DIR = "ledger"
HEAD_PATH = os.path.join(LEDGER_DIR, "latest.json")


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_oracle_bytes() -> bytes:
    req = urllib.request.Request(
        ORACLE_URL,
        headers={"Accept": "application/json", "User-Agent": "OCEI-Ledger-Bot/2.3"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def main() -> None:
    os.makedirs(LEDGER_DIR, exist_ok=True)
    raw_bytes = fetch_oracle_bytes()
    payload = json.loads(raw_bytes.decode("utf-8"))

    now = datetime.now(timezone.utc)
    recorded_utc = now.isoformat().replace("+00:00", "Z")
    month_file = os.path.join(LEDGER_DIR, f"{now.strftime('%Y-%m')}.jsonl")

    prev_seq = 0
    prev_hash = GENESIS_HASH
    spot_window = []
    if os.path.exists(HEAD_PATH):
        with open(HEAD_PATH, "r", encoding="utf-8") as f:
            head = json.load(f)
            prev_seq = int(head.get("sequence", 0))
            prev_hash = head.get("ledger_entry_hash", GENESIS_HASH)
            spot_window = list(head.get("rolling_24h_spot_window", []))

    ocei = payload.get("ocei_standard", {})
    sw = payload.get("space_weather_and_young_daly_checkpointing", {})
    grids = payload.get("live_terrestrial_spot_grids", {})
    cred = payload.get("credit_underwriting_and_covenants", {})
    att = payload.get("attestation", {})
    mr = ocei.get("multi_regime_comparison", {})

    spot = float(ocei.get("ocei_spot_realtime_score", 0.0))
    spot_window = (spot_window + [spot])[-24:]
    mean_24h = round(sum(spot_window) / len(spot_window), 4)

    epex = grids.get("epex_europe", {})
    summary = {
        "schema_version": payload.get("schema_version", "2.3.0"),
        "ocei_spot": spot,
        "ocei_structural": ocei.get("ocei_structural_5yr_score"),
        "ocei_twap_60m": ocei.get("ocei_twap_60m_settlement_score"),
        "twap_60m_source": ocei.get("twap_60m_source"),
        "vleo_320km_score": mr.get("vleo_320km_self_cleaning_edge", {}).get("score"),
        "terrestrial_tier4_score": ocei.get("terrestrial_tier4_grid_score"),
        "net_orbital_spread_bps": ocei.get("net_orbital_spread_bps"),
        "breakeven_grid_usd_mwh": ocei.get("breakeven_grid_usd_mwh"),
        "dispatch_signal": ocei.get("arbitrage_dispatch_signal"),
        "dispatch_directive": ocei.get("dispatch_directive"),
        "confidence_score": ocei.get("confidence_score"),
        "rolling_24h_mean_spot": mean_24h,
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
        "live_terrestrial_spot_grids": grids,
        "live_terrestrial_spot": {
            "market": epex.get("market", "EPEX_SPOT_DE_LU"),
            "source": epex.get("source"),
            "slot_utc": epex.get("slot_utc"),
            "price_eur_mwh": epex.get("price_native"),
            "price_usd_mwh_est": epex.get("price_usd_mwh"),
            "multiple_vs_orbital_breakeven": epex.get("multiple_vs_orbital_breakeven"),
        },
        "covenant_triggers": cred.get("covenant_triggers", {}),
    }

    entry_core = {
        "schema": "ocei.ledger.entry.v2",
        "sequence": prev_seq + 1,
        "recorded_utc": recorded_utc,
        "prev_ledger_hash": prev_hash,
        "oracle_state_hash_sha256": att.get("state_hash_sha256"),
        "oracle_signature_es256": att.get("signature"),
        "raw_payload_sha256": sha256_hex(raw_bytes),
        "jwks_kid": att.get("key_id"),
        "summary": summary,
    }
    entry_hash = sha256_hex(canonical_json(entry_core).encode("utf-8"))
    entry = dict(entry_core)
    entry["ledger_entry_hash"] = entry_hash

    with open(month_file, "a", encoding="utf-8") as f:
        f.write(canonical_json(entry) + "\n")

    head_out = {
        "schema": "ocei.ledger.head.v1",
        "sequence": entry["sequence"],
        "recorded_utc": recorded_utc,
        "ledger_file": month_file.replace("\\", "/"),
        "prev_ledger_hash": prev_hash,
        "ledger_entry_hash": entry_hash,
        "oracle_state_hash_sha256": att.get("state_hash_sha256"),
        "raw_payload_sha256": entry["raw_payload_sha256"],
        "jwks_kid": att.get("key_id"),
        "summary": summary,
        "rolling_24h_spot_window": spot_window,
    }
    with open(HEAD_PATH, "w", encoding="utf-8") as f:
        json.dump(head_out, f, indent=2)
        f.write("\n")

    print(f"Appended sequence={entry['sequence']} kid={entry['jwks_kid']} spot={spot} hash={entry_hash[:12]}")


if __name__ == "__main__":
    main()
