# OCEI™ v2.3 — Orbital Compute Efficiency Index & Live Arbitrage Oracle (MCP / A2A / Prometheus)

[![OCEI v2.3 Live Oracle](https://orbitcompute.ai/v1/index/ocei/badge.svg)](https://orbitcompute.ai/ocei)
[![DOI](https://img.shields.io/badge/Zenodo%20DOI-10.5281%2Fzenodo.24181722-38bdf8.svg)](https://doi.org/10.5281/zenodo.24181722)
[![Protocol](https://img.shields.io/badge/MCP%20%7C%20A2A%20%7C%20Prometheus-Zero--Auth-10b981.svg)](https://orbitcompute.ai/v1/openapi.json)

Official reference repository, cryptographic audit ledger, Kubernetes/KEDA manifests, and zero-dependency Python SDK for **[OrbitCompute.ai](https://orbitcompute.ai)** — the vendor-neutral, cryptographically attested (**RFC 8785 + ECDSA P-256**) control plane comparing orbital AI compute shells (`650 km Dawn-Dusk SSO`, `320 km Self-Cleaning VLEO`, `550 km LEO`, `1,500 km MEO`) against terrestrial utility grids.

## What Is New in `v2.3.0`
- **Cloudflare D1 Empirical Persistence (`15m` Cron):** True empirical 60-minute settlement TWAP (`D1_EMPIRICAL_60M`) and rolling 30-day covenant availability at `GET /v1/telemetry/history`.
- **3 Live Wholesale Spot Electricity Hubs:** Real-time arbitrage across **ERCOT Texas** (`HB_HUBAVG`), **PJM Northern Virginia** (`WESTERN HUB`), and **EPEX Spot Europe** (`DE-LU`) at `GET /v1/telemetry/live-grids`.
- **Production Hardware-Isolated ES256 Key (`ocei-es256-global-v2.3`):** Multi-year public key retention (including retired `v2.2` key) at `/.well-known/jwks.json`.
- **4-Tool MCP Server + A2A v1.0 + Prometheus `/metrics`:** Strictly separated tool schemas, native A2A `message/send` (`/a2a`), `/.well-known/agents.json`, and KEDA/Kubernetes autoscaling manifests (`k8s/keda-orbital-scaler.yaml`).
- **Expanded Physics & Credit Underwriting Kernel:** Adds `terafab_370k` high-Tj silicon, `starship_v4` / `new_glenn_9x4` launch elasticity, Turyshev communication-intensity Gamma (`bit/J`) and `deployed_mass_kg_per_it_kw` (`m_kW`), hardware attrition stress (`3.5%` / `9.0%`), `$/W` payback, and binary parametric covenant triggers.

## Executable MCP Server (Zero-Auth, Streamable HTTP)

Connect any MCP client (Claude, Cursor, Windsurf, custom agents) directly to:

```json
{
  "mcpServers": {
    "ocei-oracle": {
      "url": "https://orbitcompute.ai/mcp"
    }
  }
}
```

| MCP Tool | Purpose |
| :--- | :--- |
| `evaluate_orbital_compute_regime` | Full 4-pillar physics, 5-yr TCO, `$/W` payback, Turyshev Gamma, attrition stress & credit underwriting audit |
| `compute_arbitrage_dispatch` | Fast binary go/no-go grid-vs.-orbit dispatch against custom `$/MWh` or live `ercot` / `pjm` / `epex` hubs |
| `solve_optimal_workload_allocation` | Multi-shell percentage solver (`SSO 650 km` / `VLEO 320 km` / `Earth Spot`) with latency & downlink constraints |
| `get_ocei_history_and_live_grids` | Cloudflare D1 empirical 15-min history, true 60m TWAP, 30d covenant availability & 3 live wholesale grids |

## Core Protocol Endpoints
- **Control Room & Simulator:** `https://orbitcompute.ai/`
- **Formal Mathematical Specification:** `https://orbitcompute.ai/ocei` (`https://orbitcompute.ai/ocei.md`)
- **Institutional Reference Dossier:** `https://orbitcompute.ai/dossier`
- **IOSCO Governance Charter:** `https://orbitcompute.ai/governance` ([GOVERNANCE.md](./GOVERNANCE.md))
- **Live Attested Index & Compact M2M:** `GET /v1/index/ocei` | `GET /v1/index/ocei?format=compact`
- **D1 Time-Series & Live Grids:** `GET /v1/telemetry/history` | `GET /v1/telemetry/live-grids`
- **A2A v1.0 & Discovery:** `POST /a2a` | `/.well-known/agent-card.json` | `/.well-known/agents.json` | `/v1/openapi.json`
- **Prometheus / KEDA Metrics:** `GET /metrics` (see [k8s/keda-orbital-scaler.yaml](https://github.com/Mr-Didi/mcp-ocei-oracle/blob/main/k8s/keda-orbital-scaler.yaml))

## Quickstart: Python SDK & Cryptographic Verification

```python
from sdk.ocei_router import OceiOracleClient, verify_state_hash

client = OceiOracleClient()
grids = client.get_live_grids()
assert verify_state_hash(grids)["sha256_match"] is True
print(grids["live_terrestrial_spot_grids"]["ercot_texas"])
```

Full cryptographic and hash-chain verification instructions: [`AUDIT_VERIFICATION.md`](./AUDIT_VERIFICATION.md).

## Citation

```bibtex
@techreport{spatialcomputeholdings2026ocei,
  author      = {{Spatial Compute Holdings // OrbitCompute Data Consortium}},
  title       = {{OCEI v2.3: Orbital Compute Efficiency Index — Deterministic Thermodynamic, Radiative, Optical, Credit-Underwriting, and Token-Economic Reference Model}},
  institution = {OrbitCompute.ai},
  year        = {2026},
  doi         = {10.5281/zenodo.24181722},
  url         = {https://orbitcompute.ai/ocei}
}
```
