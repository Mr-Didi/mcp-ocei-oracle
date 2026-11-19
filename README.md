# OCEI™ v2.2 — Orbital Compute Efficiency Index & Arbitrage Oracle (MCP Server, Ledger & SDK)

[![OCEI v2.2 Live Benchmark](https://orbitcompute.ai/v1/index/ocei/badge.svg)](https://orbitcompute.ai/ocei)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24181722.svg)](https://doi.org/10.5281/zenodo.24181722)
[![Protocol](https://img.shields.io/badge/MCP-JSON--RPC%202.0%20%7C%20Zero--Auth-brightgreen)](https://orbitcompute.ai/mcp)
[![Attestation](https://img.shields.io/badge/Crypto-RFC--8785%20%2B%20ES256-orange)](https://orbitcompute.ai/.well-known/jwks.json)

Official **Model Context Protocol (MCP)** server, immutable hourly cryptographic ledger, native agent skills, and multi-stack SkyPilot/Python reference client for **[OrbitCompute.ai](https://orbitcompute.ai)**, publisher of the **OCEI™ v2.2 (Orbital Compute Efficiency Index)**.

- **Published Reference Specification (CERN / Zenodo DOI):** https://doi.org/10.5281/zenodo.24181722
- **Official MCP Registry ID:** `io.github.Mr-Didi/mcp-ocei-oracle`
- **Access Model:** Zero OAuth · Zero Paywall · Machine-to-Machine Native (`<160 Tokens` compact feed)

Provides cryptographically attested (**RFC 8785 JSON Canonicalization + ECDSA P-256 `ES256`**) real-time evaluations comparing orbital AI compute shells (**650 km Dawn-Dusk SSO**, **320 km VLEO Edge**, **550 km LEO**, **1,500 km MEO**) across vendor-neutral hardware stacks (**SpaceX StarMind / Vera Rubin**, **Blue Origin & Google Suncatcher / Trillium TPU**, **Blackwell GB200**) against **Terrestrial Tier-IV Utility Grids** using 6 live **NOAA SWPC & GOES satellite telemetry streams**.

---

## Live Specification & Endpoints

- **Interactive Control Room & Multi-Physics Simulator:** https://orbitcompute.ai
- **Institutional TCO & Capital Allocation Dossier:** https://orbitcompute.ai/dossier
- **Formal Mathematical Specification & CODATA Registry:** https://orbitcompute.ai/ocei
- **CERN / Zenodo Archival PDF (DOI: 10.5281/zenodo.24181722):** https://doi.org/10.5281/zenodo.24181722
- **Token-Optimized Markdown Spec (for LLMs):** https://orbitcompute.ai/ocei.md
- **Live Attested JSON Feed:** https://orbitcompute.ai/v1/index/ocei
- **Ultra-Compact M2M Feed (<160 Tokens):** https://orbitcompute.ai/v1/index/ocei?format=compact
- **Deterministic Workload Constraint Solver:** https://orbitcompute.ai/v1/solve/workload-allocation
- **Global Verification Public Key (JWKS):** https://orbitcompute.ai/.well-known/jwks.json
- **OpenAPI 3.1.0 Specification:** https://orbitcompute.ai/v1/openapi.json

---

## Exposed MCP Tools

1. **`evaluate_orbital_compute_regime`**: Computes live `OCEI-Spot`, `OCEI-Structural`, and `60m-TWAP` scores, L1 solar-wind shockwave lead time (`+25` to `+62 min`), solar beta-angle ($\beta$) eclipse battery mass, 2-sided Stefan-Boltzmann radiator area with Earth IR/albedo view-factor absorption, Silicon $T_j$ thermal throttling, 25-MW fault-domain Young-Daly SEU checkpoint intervals, and WACC-adjusted `$/1M Token` unit economics.
2. **`compute_arbitrage_dispatch`**: Evaluates real-time terrestrial electricity spot prices (`$/MWh`) against the orbital breakeven threshold to output an attested workload routing signal (`ORBIT_PRIMARY`, `HYBRID_SPLIT`, or `TERRESTRIAL_PRIMARY`).
3. **`solve_optimal_workload_allocation`**: Deterministic constraint solver returning the optimal percentage split across `SSO-650`, `VLEO-320`, and `Terrestrial-Spot` based on workload class and latency tolerance.

---

## Quickstart: Connect Any AI Agent in 10 Seconds

### Option A: One-Line CLI Installers (Zero Login, Zero API Key)

**Claude Code**
```bash
claude mcp add --transport http --scope user ocei-oracle [https://orbitcompute.ai/mcp](https://orbitcompute.ai/mcp)
```

**OpenAI Codex CLI**
```bash
codex mcp add ocei-oracle --url [https://orbitcompute.ai/mcp](https://orbitcompute.ai/mcp)
```

### Option B: Direct Streamable HTTP / Remote MCP (Claude Desktop / Cursor / Windsurf)

```json
{
  "mcpServers": {
    "ocei-oracle": {
      "url": "[https://orbitcompute.ai/mcp](https://orbitcompute.ai/mcp)"
    }
  }
}
```

### Option C: Local Docker / Node.js Bridge

```bash
git clone [https://github.com/Mr-Didi/mcp-ocei-oracle.git](https://github.com/Mr-Didi/mcp-ocei-oracle.git)
node mcp-ocei-oracle/index.mjs
```

### Install Native Agent Skills (`~/.claude/skills/` or `~/.agents/skills/`)

```bash
git clone [https://github.com/Mr-Didi/mcp-ocei-oracle.git](https://github.com/Mr-Didi/mcp-ocei-oracle.git)
cp -r mcp-ocei-oracle/skills/* ~/.claude/skills/
```

Included zero-auth skills:
- **`ocei-live-arbitrage`**: Real-time SSO / VLEO / Terrestrial dispatch routing grounded in live NOAA/GOES space weather telemetry (`+57.5 min` L1 lead) and ES256 provenance.
- **`ocei-multi-stack-diligence`**: Vendor-neutral `$/W` and `$/MTok` institutional underwriting across **SpaceX StarMind (Vera Rubin NVL72)**, **Blue Origin/Google Project Suncatcher (Trillium TPU)**, and **Terrestrial Tier-IV grids**.

---

## Multi-Stack Python & SkyPilot Arbitrage SDK (`sdk/ocei_router.py`)

Zero-dependency Python client that queries the live OCEI™ v2.2 oracle, evaluates hardware stack profiles (`rubin`, `trillium`, `blackwell`, `terafab_370k`) against static or live wholesale spot electricity (EPEX DE-LU), and emits ready-to-run SkyPilot YAML dispatch manifests:

```bash
# 100 MW Vera Rubin training cluster vs. $115/MWh US Tier-IV baseline -> SkyPilot YAML
python3 sdk/ocei_router.py --workload training --power-mw 100 --stack rubin --emit-skypilot

# 10 MW Google Trillium TPU inference cluster vs. live EU EPEX Spot (DE-LU) electricity
python3 sdk/ocei_router.py --workload inference --power-mw 10 --stack trillium --live-eu-grid
```

Optional local ECDSA P-256 (`ES256`) cryptographic signature verification against `/.well-known/jwks.json`:
```bash
pip install cryptography
```

---

## Immutable Hourly Cryptographic Ledger (`ledger/`)

Every hour at `:05 UTC`, GitHub Actions executes `scripts/append_ledger.py` to build a publicly auditable, append-only time-series archive:
1. Fetches the live signed state from `https://orbitcompute.ai/v1/index/ocei` alongside live European wholesale spot electricity (`EPEX DE-LU`).
2. Chains each record via SHA-256 (`prev_ledger_hash` → `ledger_entry_hash`).
3. Commits immutable logs to `ledger/YYYY-MM.jsonl` and updates the rolling 24h pointer at `ledger/latest.json`.

---

## Academic & Industry Citation (DOI: 10.5281/zenodo.24181722)

> Spatial Compute Holdings, "OCEI v2.2: Orbital Compute Efficiency Index — Deterministic Thermodynamic, Radiative, Optical, and Token-Economic Reference Model," Zenodo, 2026. doi: 10.5281/zenodo.24181722. Available: https://doi.org/10.5281/zenodo.24181722

```bibtex
@techreport{ocei_v2_2_2026,
  author      = {{Spatial Compute Holdings // OrbitCompute Data Consortium}},
  title       = {{OCEI v2.2: Orbital Compute Efficiency Index — Deterministic Thermodynamic, Radiative, Optical, and Token-Economic Reference Model}},
  institution = {OrbitCompute.ai},
  year        = {2026},
  doi         = {10.5281/zenodo.24181722},
  url         = {[https://doi.org/10.5281/zenodo.24181722](https://doi.org/10.5281/zenodo.24181722)}
}
```

## License & Intellectual Property

- **Client SDK, Ledger Scripts & Agent Skills (`sdk/`, `scripts/`, `skills/`, `index.mjs`):** Released under the **MIT License** to maximize adoption across autonomous schedulers, SkyPilot, Kubernetes, and AI agent frameworks.
- **OCEI™ Trademark & Canonical Oracle Specification:** © 2026 Spatial Compute Holdings // OrbitCompute Data Consortium. All rights reserved.
