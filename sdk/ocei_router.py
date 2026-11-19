#!/usr/bin/env python3
"""
OCEI™ v2.2 Multi-Stack Orbital Compute & SkyPilot Arbitrage SDK
Zero-auth client for https://orbitcompute.ai (DOI: 10.5281/zenodo.24181722).

Usage:
  python3 sdk/ocei_router.py --workload training --power-mw 100 --stack rubin --emit-skypilot
  python3 sdk/ocei_router.py --workload inference --power-mw 10 --stack trillium --live-eu-grid
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

OCEI_BASE = "https://orbitcompute.ai"
EU_SPOT_URL = "https://api.energy-charts.info/price?bzn=DE-LU"


@dataclass(frozen=True)
class OrbitalStackProfile:
    stack_id: str
    vendor_stack: str
    node_power_kw: float
    radiator_temp_k: float
    net_rejection_w_m2: float
    breakeven_grid_usd_mwh: float
    orbital_tco_usd_per_mtok: float
    earth_tco_usd_per_mtok: float
    preferred_shell: str


HARDWARE_PROFILES: dict[str, OrbitalStackProfile] = {
    "rubin": OrbitalStackProfile(
        stack_id="rubin",
        vendor_stack="SpaceX StarMind / Nvidia Vera Rubin NVL72",
        node_power_kw=250.0,
        radiator_temp_k=353.15,
        net_rejection_w_m2=1186.8,
        breakeven_grid_usd_mwh=28.41,
        orbital_tco_usd_per_mtok=0.5135,
        earth_tco_usd_per_mtok=0.9538,
        preferred_shell="650km_DAWN_DUSK_SSO",
    ),
    "trillium": OrbitalStackProfile(
        stack_id="trillium",
        vendor_stack="Blue Origin New Glenn / Google Suncatcher Trillium TPU v6e",
        node_power_kw=125.0,
        radiator_temp_k=353.15,
        net_rejection_w_m2=1186.8,
        breakeven_grid_usd_mwh=26.80,
        orbital_tco_usd_per_mtok=0.5310,
        earth_tco_usd_per_mtok=0.9538,
        preferred_shell="650km_DAWN_DUSK_SSO",
    ),
    "blackwell": OrbitalStackProfile(
        stack_id="blackwell",
        vendor_stack="Orbital Commercial / Nvidia Blackwell GB200 NVL72",
        node_power_kw=120.0,
        radiator_temp_k=353.15,
        net_rejection_w_m2=1186.8,
        breakeven_grid_usd_mwh=25.90,
        orbital_tco_usd_per_mtok=0.5480,
        earth_tco_usd_per_mtok=0.9538,
        preferred_shell="650km_DAWN_DUSK_SSO",
    ),
    "terafab_370k": OrbitalStackProfile(
        stack_id="terafab_370k",
        vendor_stack="Custom High-Tj Vacuum Silicon (370K Radiator Loop)",
        node_power_kw=250.0,
        radiator_temp_k=370.0,
        net_rejection_w_m2=1458.0,
        breakeven_grid_usd_mwh=21.50,
        orbital_tco_usd_per_mtok=0.4790,
        earth_tco_usd_per_mtok=0.9538,
        preferred_shell="650km_DAWN_DUSK_SSO",
    ),
}


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "OCEI-Arbitrage-SDK/1.1 (+https://orbitcompute.ai)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class OCEIArbitrageRouter:
    """Zero-auth deterministic compute router backed by the live OCEI™ v2.2 oracle."""

    def __init__(self, base_url: str = OCEI_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    def fetch_live_index(self, compact: bool = False) -> dict[str, Any]:
        suffix = "?format=compact" if compact else ""
        return _http_get_json(f"{self.base_url}/v1/index/ocei{suffix}")

    def fetch_jwks(self) -> dict[str, Any]:
        return _http_get_json(f"{self.base_url}/.well-known/jwks.json")

    def fetch_solver(self, workload: str, grid_usd_mwh: float, power_mw: float) -> dict[str, Any] | None:
        qs = urllib.parse.urlencode(
            {"workload": workload, "grid_price_mwh": grid_usd_mwh, "power_mw": power_mw}
        )
        try:
            return _http_get_json(f"{self.base_url}/v1/solve/workload-allocation?{qs}")
        except Exception:
            return None

    def fetch_live_eu_grid_usd_mwh(self, eur_usd: float = 1.08) -> float | None:
        try:
            data = _http_get_json(EU_SPOT_URL, timeout=10)
            timestamps = data.get("unix_seconds") or []
            prices = data.get("price") or []
            now_ts = int(dt.datetime.now(dt.timezone.utc).timestamp())
            latest_eur = None
            for ts, val in zip(timestamps, prices):
                if val is not None and ts <= now_ts:
                    latest_eur = float(val)
            return round(latest_eur * eur_usd, 2) if latest_eur is not None else None
        except Exception:
            return None

    def verify_es256_attestation(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Verifies RFC-8785 / ECDSA P-256 (ES256) attestation against /.well-known/jwks.json
        when `cryptography` is installed, and always returns the SHA-256 payload digest.
        """
        att = payload.get("attestation") or {}
        sig_b64 = att.get("signature")
        key_id = att.get("key_id") or att.get("kid")
        oracle_hash = att.get("state_hash_sha256")
        unsigned = {k: v for k, v in payload.items() if k != "attestation"}
        unsigned_bytes = _canonical_bytes(unsigned)
        computed_unsigned_hash = hashlib.sha256(unsigned_bytes).hexdigest()
        full_digest = hashlib.sha256(_canonical_bytes(payload)).hexdigest()

        if not sig_b64:
            return {
                "verified": False,
                "reason": "no_signature_field",
                "payload_sha256": full_digest,
            }

        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

            jwks = self.fetch_jwks()
            key_dict = next(
                (k for k in jwks.get("keys", []) if not key_id or k.get("kid") == key_id),
                (jwks.get("keys") or [None])[0],
            )
            if not key_dict:
                return {
                    "verified": False,
                    "reason": "jwks_key_not_found",
                    "key_id": key_id,
                    "payload_sha256": full_digest,
                }

            def b64url_decode(val: str) -> bytes:
                pad = "=" * (-len(val) % 4)
                return base64.urlsafe_b64decode(val + pad)

            x_int = int.from_bytes(b64url_decode(key_dict["x"]), "big")
            y_int = int.from_bytes(b64url_decode(key_dict["y"]), "big")
            pub_key = ec.EllipticCurvePublicNumbers(x_int, y_int, ec.SECP256R1()).public_key()

            sig_bytes = b64url_decode(sig_b64)
            if len(sig_bytes) == 64:
                r = int.from_bytes(sig_bytes[:32], "big")
                s = int.from_bytes(sig_bytes[32:], "big")
                der_sig = encode_dss_signature(r, s)
            else:
                der_sig = sig_bytes

            verified = False
            verified_mode = None
            for mode, msg in (
                ("canonical_unsigned_json", unsigned_bytes),
                ("oracle_state_hash_hex", (oracle_hash or "").encode("utf-8")),
            ):
                if not msg:
                    continue
                try:
                    pub_key.verify(der_sig, msg, ec.ECDSA(hashes.SHA256()))
                    verified = True
                    verified_mode = mode
                    break
                except Exception:
                    continue

            return {
                "verified": verified,
                "verified_mode": verified_mode,
                "key_id": key_dict.get("kid"),
                "oracle_state_hash_sha256": oracle_hash,
                "computed_unsigned_sha256": computed_unsigned_hash,
                "hash_matches_unsigned": (oracle_hash == computed_unsigned_hash) if oracle_hash else None,
                "payload_sha256": full_digest,
            }
        except ImportError:
            return {
                "verified": None,
                "reason": "install `pip install cryptography` for local ECDSA P-256 verification",
                "key_id": key_id,
                "oracle_state_hash_sha256": oracle_hash,
                "payload_sha256": full_digest,
            }
        except Exception as exc:
            return {
                "verified": False,
                "reason": f"signature_check_error:{exc}",
                "key_id": key_id,
                "payload_sha256": full_digest,
            }

    def route(
        self,
        workload: str = "training",
        power_mw: float = 100.0,
        stack: str = "rubin",
        grid_usd_mwh: float = 115.0,
    ) -> dict[str, Any]:
        profile = HARDWARE_PROFILES[stack]
        live = self.fetch_live_index(compact=False)
        attest = self.verify_es256_attestation(live)
        remote_solver = self.fetch_solver(workload=workload, grid_usd_mwh=grid_usd_mwh, power_mw=power_mw)

        std = live.get("ocei_standard") or {}
        multi = std.get("multi_regime_comparison") or {}
        sw = live.get("space_weather_and_young_daly_checkpointing") or {}

        ocei_spot = float(std.get("ocei_spot_realtime_score", 950.0))
        ocei_struct = float(std.get("ocei_structural_5yr_score", 975.0))
        ocei_twap = float(std.get("ocei_twap_60m_settlement_score", ocei_spot))
        vleo_score = float((multi.get("vleo_320km_self_cleaning_edge") or {}).get("score", 940.0))
        live_breakeven = (
            float(std["breakeven_grid_usd_mwh"])
            if stack == "rubin" and "breakeven_grid_usd_mwh" in std
            else profile.breakeven_grid_usd_mwh
        )

        storm_trigger = bool(sw.get("pre_emptive_checkpoint_trigger", False)) or ocei_spot < 650.0
        grid_beats_orbit = grid_usd_mwh <= live_breakeven

        if storm_trigger:
            regime = "TERRESTRIAL_STORM_FAILOVER"
            split = {"orbit_sso_pct": 15, "orbit_vleo_pct": 0, "earth_spot_pct": 85}
        elif grid_beats_orbit:
            regime = "TERRESTRIAL_SPOT_ARBITRAGE"
            split = {"orbit_sso_pct": 25, "orbit_vleo_pct": 10, "earth_spot_pct": 65}
        elif workload == "inference":
            regime = "HYBRID_VLEO_EDGE_PRIMARY"
            split = {"orbit_sso_pct": 20, "orbit_vleo_pct": 65, "earth_spot_pct": 15}
        else:
            regime = "ORBIT_SSO_PRIMARY"
            split = {"orbit_sso_pct": 85, "orbit_vleo_pct": 10, "earth_spot_pct": 5}

        nodes_required = int(round((power_mw * 1000.0) / profile.node_power_kw))
        return {
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "oracle": f"{self.base_url}/v1/index/ocei",
            "doi": "10.5281/zenodo.24181722",
            "stack_profile": profile.vendor_stack,
            "workload": workload,
            "power_mw": power_mw,
            "nodes_required": nodes_required,
            "terrestrial_grid_usd_mwh": grid_usd_mwh,
            "orbital_breakeven_usd_mwh": live_breakeven,
            "ocei_spot": ocei_spot,
            "ocei_structural": ocei_struct,
            "ocei_twap_60m": ocei_twap,
            "vleo_320km_score": vleo_score,
            "oracle_dispatch_signal": std.get("arbitrage_dispatch_signal"),
            "net_availability_pct": sw.get("net_effective_compute_availability_pct"),
            "l1_lead_time_min": sw.get("l1_shockwave_lead_time_min"),
            "dispatch_regime": regime,
            "allocation_split_pct": split,
            "attestation": attest,
            "remote_solver_payload": remote_solver,
        }


def render_skypilot_yaml(decision: dict[str, Any]) -> str:
    regime = decision["dispatch_regime"]
    use_earth_spot = regime in {"TERRESTRIAL_STORM_FAILOVER", "TERRESTRIAL_SPOT_ARBITRAGE"}
    cloud_hint = "aws" if use_earth_spot else "kubernetes"
    spot_flag = "true" if use_earth_spot else "false"
    return f"""# Auto-generated by OCEI™ v2.2 Multi-Stack Arbitrage SDK (https://orbitcompute.ai)
# DOI: {decision['doi']}
# Timestamp: {decision['timestamp_utc']}
# Live OCEI-Spot: {decision['ocei_spot']} | TWAP-60m: {decision['ocei_twap_60m']} | VLEO-320: {decision['vleo_320km_score']}
# Young-Daly Availability: {decision['net_availability_pct']}% | L1 Lead: +{decision['l1_lead_time_min']}m
# Terrestrial Grid: ${decision['terrestrial_grid_usd_mwh']}/MWh vs Breakeven: ${decision['orbital_breakeven_usd_mwh']}/MWh
# Dispatch Regime: {regime}
# Payload SHA-256: {decision['attestation']['payload_sha256']}

name: ocei-{decision['workload']}-{regime.lower().replace('_', '-')}

resources:
  cloud: {cloud_hint}
  use_spot: {spot_flag}
  accelerators: H200:8
  labels:
    ocei.orbitcompute.ai/regime: "{regime}"
    ocei.orbitcompute.ai/spot-score: "{decision['ocei_spot']}"
    ocei.orbitcompute.ai/orbit-sso-pct: "{decision['allocation_split_pct']['orbit_sso_pct']}"
    ocei.orbitcompute.ai/orbit-vleo-pct: "{decision['allocation_split_pct']['orbit_vleo_pct']}"
    ocei.orbitcompute.ai/earth-spot-pct: "{decision['allocation_split_pct']['earth_spot_pct']}"

envs:
  OCEI_ORACLE_URL: "https://orbitcompute.ai/mcp"
  OCEI_DISPATCH_REGIME: "{regime}"
  OCEI_YOUNG_DALY_CHECKPOINTING: "enabled"

run: |
  echo "Executing {decision['workload']} under OCEI regime=${{OCEI_DISPATCH_REGIME}} (Spot={decision['ocei_spot']})"
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="OCEI™ v2.2 Orbital Compute Arbitrage & SkyPilot Router")
    parser.add_argument("--workload", choices=["training", "inference", "batch_reasoning"], default="training")
    parser.add_argument("--power-mw", type=float, default=100.0)
    parser.add_argument("--stack", choices=list(HARDWARE_PROFILES.keys()), default="rubin")
    parser.add_argument("--grid-usd-mwh", type=float, default=115.0)
    parser.add_argument("--live-eu-grid", action="store_true", help="Fetch live EPEX Spot DE-LU price")
    parser.add_argument("--emit-skypilot", action="store_true", help="Print SkyPilot YAML dispatch manifest")
    args = parser.parse_args()

    router = OCEIArbitrageRouter()
    grid_price = args.grid_usd_mwh
    if args.live_eu_grid:
        live_price = router.fetch_live_eu_grid_usd_mwh()
        if live_price is not None:
            grid_price = live_price

    decision = router.route(
        workload=args.workload,
        power_mw=args.power_mw,
        stack=args.stack,
        grid_usd_mwh=grid_price,
    )

    if args.emit_skypilot:
        print(render_skypilot_yaml(decision))
    else:
        print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
