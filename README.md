# OCEI™ v2.2 — Orbital Compute Efficiency Index & Arbitrage Oracle (MCP Server)

[![OCEI v2.2 Live Benchmark](https://orbitcompute.ai/v1/index/ocei/badge.svg)](https://orbitcompute.ai/ocei)

Official **Model Context Protocol (MCP)** server and deterministic reference client for **[OrbitCompute.ai](https://orbitcompute.ai)**, publisher of the **OCEI™ v2.2 (Orbital Compute Efficiency Index)**.

Provides cryptographically attested (**RFC 8785 JSON Canonicalization + ECDSA P-256 `ES256`**) real-time evaluations comparing orbital AI compute shells (**650 km Dawn-Dusk SSO**, **320 km VLEO Edge**, **550 km LEO**, **1,500 km MEO**) against **Terrestrial Tier-IV Utility Grids** using 6 live **NOAA SWPC & GOES satellite telemetry streams**.

## Live Specification & Endpoints

- **Interactive Control Room & Multi-Physics Simulator:** [https://orbitcompute.ai](https://orbitcompute.ai)
- **Formal Mathematical Specification & CODATA Registry:** [https://orbitcompute.ai/ocei](https://orbitcompute.ai/ocei)
- **Token-Optimized Markdown Spec (for LLMs):** [https://orbitcompute.ai/ocei.md](https://orbitcompute.ai/ocei.md)
- **Live Attested JSON Feed:** [https://orbitcompute.ai/v1/index/ocei](https://orbitcompute.ai/v1/index/ocei)
- **Ultra-Compact M2M Feed (<160 Tokens):** [https://orbitcompute.ai/v1/index/ocei?format=compact](https://orbitcompute.ai/v1/index/ocei?format=compact)
- **Global Verification Public Key (JWKS):** [https://orbitcompute.ai/.well-known/jwks.json](https://orbitcompute.ai/.well-known/jwks.json)
- **OpenAPI 3.1.0 Specification:** [https://orbitcompute.ai/v1/openapi.json](https://orbitcompute.ai/v1/openapi.json)

## Exposed MCP Tools

1. **`evaluate_orbital_compute_regime`**: Computes live OCEI-Spot, OCEI-Structural, and 60m-TWAP scores, L1 solar-wind shockwave lead time (+25 to +62 min), solar beta-angle (beta) eclipse battery mass, 2-sided Stefan-Boltzmann radiator area with Earth IR/albedo view-factor absorption, Silicon Tj thermal throttling, 25-MW fault-domain Young-Daly SEU checkpoint intervals, and WACC-adjusted $/1M Token unit economics.
2. **`compute_arbitrage_dispatch`**: Evaluates real-time terrestrial electricity spot prices ($/MWh) against the orbital breakeven threshold to output an attested workload routing signal (`ORBIT_PRIMARY`, `HYBRID_SPLIT`, or `TERRESTRIAL_PRIMARY`).
3. **`solve_optimal_workload_allocation`**: Deterministic constraint solver returning the optimal percentage split across `SSO-650`, `VLEO-320`, and `Terrestrial-Spot` based on workload class and latency tolerance.

## Quickstart (Claude Desktop / Cursor / Windsurf / MCP Clients)

### Option A: Direct Streamable HTTP / Remote MCP

    {
      "mcpServers": {
        "ocei-oracle": {
          "url": "[https://orbitcompute.ai/mcp](https://orbitcompute.ai/mcp)"
        }
      }
    }

### Option B: Local Docker / Node.js Bridge

    git clone [https://github.com/Mr-Didi/mcp-ocei-oracle.git](https://github.com/Mr-Didi/mcp-ocei-oracle.git)
    node mcp-ocei-oracle/index.mjs

## Standard Citation

> Spatial Compute Holdings, "OCEI v2.2: Orbital Compute Efficiency Index — Deterministic Thermodynamic, Radiative & Arbitrage Reference Model," OrbitCompute.ai, 2026. Available: [https://orbitcompute.ai/ocei](https://orbitcompute.ai/ocei)
