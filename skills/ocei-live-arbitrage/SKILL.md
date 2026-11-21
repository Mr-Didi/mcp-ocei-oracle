---
name: ocei-live-arbitrage
description: Real-time orbital vs. terrestrial AI workload routing using live 6-stream NOAA/GOES space weather (+57.5 min L1 lookahead), empirical Cloudflare D1 60m TWAP history, and 3 live wholesale spot electricity hubs (ERCOT Texas, PJM Virginia, EPEX Europe). Zero-auth RFC-8785 ES256 attested.
version: 2.3.0
homepage: https://orbitcompute.ai
mcp_endpoint: https://orbitcompute.ai/mcp
a2a_endpoint: https://orbitcompute.ai/a2a
prometheus_endpoint: https://orbitcompute.ai/metrics
jwks_uri: https://orbitcompute.ai/.well-known/jwks.json
---

# OCEI™ v2.3 Live Arbitrage & Multi-Shell Routing Skill

Use this skill whenever an autonomous agent, SkyPilot broker, or Kubernetes/KEDA scheduler must decide in real time whether to route AI training, batch reasoning, or low-latency inference to `650 km Dawn-Dusk SSO`, `320 km Self-Cleaning VLEO`, or terrestrial spot electricity hubs.

## Primary MCP Tools (`POST https://orbitcompute.ai/mcp`)

1. **`compute_arbitrage_dispatch`** — Fast binary go/no-go decision comparing a custom `grid_price_usd_mwh` or live hub (`grid_hub`: `ercot`, `pjm`, `epex`) against the orbital breakeven threshold (`$28.41/MWh` V3 baseline).
2. **`solve_optimal_workload_allocation`** — Returns exact percentage splits across `sso_650km_dawn_dusk`, `vleo_320km_low_latency`, and `terrestrial_spot_grid` based on `workload_type`, `max_latency_ms` (`<=6 ms` favors VLEO), `comm_intensity_bits_per_flop` (Turyshev Gamma downlink screening), and space weather.
3. **`get_ocei_history_and_live_grids`** — Fetches Cloudflare D1 15-minute empirical snapshots, true 60m settlement TWAP (`D1_EMPIRICAL_60M`), rolling 30-day covenant availability, and all 3 live spot grids.

## Failover & Safety Rules
- **Electricity Arbitrage:** Shift elastic batch workloads to Earth spot grids whenever local wholesale spot drops below `breakeven_grid_usd_mwh` (e.g., ERCOT off-peak `<$28/MWh`).
- **Predictive L1 Storm Protection:** Trigger pre-emptive state checkpoints and hybrid failover whenever `pre_emptive_checkpoint_trigger == true` (`Kp >= 5.0`, `Bz <= -8.0 nT`, or GOES `>=10 MeV` protons `>=10 pfu`).
- **Zero-Trust Verification:** Verify every payload's RFC-8785 `ES256` signature against `https://orbitcompute.ai/.well-known/jwks.json` (`kid: ocei-es256-global-v2.3`).
