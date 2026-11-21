#!/usr/bin/env python3
"""
OCEI v2.3 Zero-Dependency Python SDK & M2M Workload Router.
Supports live 3-hub spot electricity arbitrage (ERCOT, PJM, EPEX),
Cloudflare D1 empirical TWAP history, Turyshev Gamma downlink screening,
JSON-RPC 2.0 MCP tool calls, and local RFC-8785 SHA-256 state verification.
"""
import hashlib
import json
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://orbitcompute.ai"


def canonicalize_rfc8785(obj: Any) -> str:
    """Deterministic RFC-8785 / JCS canonical JSON serialization."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def verify_state_hash(attested_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Independently recomputes SHA-256 over the RFC-8785 canonical payload."""
    att = attested_payload.get("attestation", {})
    expected_hash = att.get("state_hash_sha256", "")
    unsigned = {k: v for k, v in attested_payload.items() if k != "attestation"}
    computed_hash = hashlib.sha256(canonicalize_rfc8785(unsigned).encode("utf-8")).hexdigest()
    return {
        "sha256_match": computed_hash == expected_hash,
        "computed_sha256": computed_hash,
        "expected_sha256": expected_hash,
        "key_id": att.get("key_id"),
        "algorithm": att.get("algorithm"),
        "jwks_uri": att.get("jwks_uri"),
    }


class OceiOracleClient:
    """Zero-auth M2M client for OrbitCompute.ai OCEI v2.3 Oracle."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 12.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        qs = ""
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                qs = "?" + urllib.parse.urlencode(clean)
        req = urllib.request.Request(
            f"{self.base_url}{path}{qs}",
            headers={"Accept": "application/json", "User-Agent": "ocei-python-sdk/2.3.0"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ocei-python-sdk/2.3.0",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_ocei_index(
        self,
        power_mw: float = 100,
        altitude_km: float = 650,
        beta_deg: float = 75,
        hw: str = "rubin_nvl72",
        launch_vehicle: str = "starship_v3",
        loop_temp_c: float = 80,
        grid_price_usd_mwh: Optional[float] = None,
        grid_hub: str = "baseline",
        earth_capex_factor: float = 1.0,
        annual_attrition_pct: float = 0.0,
        comm_intensity_bits_per_flop: float = 1e-8,
        storm_mode: str = "live",
        compact: bool = False,
    ) -> Dict[str, Any]:
        return self._get(
            "/v1/index/ocei",
            {
                "power_mw": power_mw,
                "altitude_km": altitude_km,
                "beta_deg": beta_deg,
                "hw": hw,
                "launch_vehicle": launch_vehicle,
                "loop_temp_c": loop_temp_c,
                "grid_price_usd_mwh": grid_price_usd_mwh,
                "grid_hub": grid_hub if grid_price_usd_mwh is None else None,
                "earth_capex_factor": earth_capex_factor,
                "annual_attrition_pct": annual_attrition_pct,
                "comm_intensity_bits_per_flop": comm_intensity_bits_per_flop,
                "storm_mode": storm_mode,
                "format": "compact" if compact else None,
            },
        )

    def get_live_grids(self) -> Dict[str, Any]:
        """Returns live ERCOT Texas, PJM Virginia, and EPEX Europe spot prices vs. orbital breakeven."""
        return self._get("/v1/telemetry/live-grids")

    def get_history(self, hours: int = 24, limit: int = 48) -> Dict[str, Any]:
        """Returns Cloudflare D1 15-minute empirical snapshots, true 60m TWAP & 30d covenant availability."""
        return self._get("/v1/telemetry/history", {"hours": hours, "limit": limit})

    def get_arbitrage_dispatch(
        self,
        grid_price_usd_mwh: Optional[float] = None,
        grid_hub: str = "ercot",
        power_mw: float = 100,
        hw: str = "rubin_nvl72",
        storm_mode: str = "live",
    ) -> Dict[str, Any]:
        return self._get(
            "/v1/arbitrage/dispatch-signal",
            {
                "power_mw": power_mw,
                "grid_price_usd_mwh": grid_price_usd_mwh,
                "grid_hub": grid_hub if grid_price_usd_mwh is None else None,
                "hw": hw,
                "storm_mode": storm_mode,
            },
        )

    def solve_allocation(
        self,
        workload_type: str = "frontier_training",
        max_latency_ms: float = 45,
        grid_price_usd_mwh: Optional[float] = None,
        grid_hub: str = "baseline",
        comm_intensity_bits_per_flop: float = 1e-8,
        storm_mode: str = "live",
    ) -> Dict[str, Any]:
        return self._get(
            "/v1/solve/workload-allocation",
            {
                "workload_type": workload_type,
                "max_latency_ms": max_latency_ms,
                "grid_price_usd_mwh": grid_price_usd_mwh,
                "grid_hub": grid_hub if grid_price_usd_mwh is None else None,
                "comm_intensity_bits_per_flop": comm_intensity_bits_per_flop,
                "storm_mode": storm_mode,
            },
        )

    def call_mcp_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invokes any of the 4 OCEI v2.3 MCP tools over Streamable HTTP JSON-RPC 2.0."""
        rpc = self._post(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments or {}},
            },
        )
        content = rpc.get("result", {}).get("content", [])
        if content and "text" in content[0]:
            return json.loads(content[0]["text"])
        return rpc


if __name__ == "__main__":
    client = OceiOracleClient()
    live = client.get_live_grids()
    check = verify_state_hash(live)
    print(json.dumps({"verification": check, "live_grids": live.get("live_terrestrial_spot_grids")}, indent=2))
