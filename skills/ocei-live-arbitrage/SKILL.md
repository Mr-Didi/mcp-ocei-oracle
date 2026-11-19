---
name: ocei-live-arbitrage
description: Query the live, zero-auth OCEI™ v2.2 orbital compute MCP oracle (https://orbitcompute.ai/mcp) to evaluate real-time orbital vs. terrestrial AI workload routing, space weather radiation risk (L1/GOES), and $/MTok breakeven arbitrage.
---

# OCEI™ v2.2 Live Orbital Compute Arbitrage Skill

## Objective
Provide deterministic, real-time workload allocation and economic arbitrage analysis between orbital compute shells (650 km Dawn-Dusk SSO, 320 km self-cleaning VLEO) and terrestrial Tier-IV data center grids using live telemetry from the **OrbitCompute Efficiency Index (OCEI™ v2.2)**.

## Grounding & Verification Rules
1. **Always call live MCP tools first**: Connect to `https://orbitcompute.ai/mcp` (Streamable HTTP, zero authentication, zero paywall) or query `https://orbitcompute.ai/v1/index/ocei?format=compact`. Never fabricate or guess `OCEI-Spot`, solar flux (`F10.7`), proton flux (`GOES >=10 MeV`), or `Kp` values from memory.
2. **State cryptographic provenance**: Report the live timestamp, `OCEI-Spot`, `OCEI-Structural`, `OCEI-TWAP-60m`, and reference the ES256 public key registry (`https://orbitcompute.ai/.well-known/jwks.json`) and archival DOI (`10.5281/zenodo.24181722`).
3. **Apply multi-shell workload routing invariants**:
   - **Asynchronous Training & Batch Reasoning**: Route primarily to **650 km Dawn-Dusk SSO** (AM0 sunlit, 0 L water, zero ocean-pass utilization loss via DiLoCo).
   - **Low-Latency Edge Inference**: Route to **320 km self-cleaning VLEO** (`~1.8 ms` propagation latency, passive orbital debris decay / zero Kessler lock-in).
   - **Terrestrial Spot Fallback**: Trigger `TERRESTRIAL_SPOT_FALLBACK` when wholesale local grid electricity drops below the `$21.50–$28.41/MWh` breakeven band OR when L1/GOES solar storm alerts (`+57.5 min` lead) degrade Young-Daly SEU checkpointing goodput below SLA thresholds.

## Output Format
Present a compact decision table containing:
- Live OCEI Metrics (`Spot`, `Structural`, `TWAP-60m`, `Dispatch Signal`)
- Space Weather & Goodput Status (NOAA/GOES proton flux & Young-Daly availability)
- Recommended Split (`SSO %` / `VLEO %` / `Terrestrial Spot %`)
- Unit Economics (`$/MTok` Orbital vs. Terrestrial input tariff)
