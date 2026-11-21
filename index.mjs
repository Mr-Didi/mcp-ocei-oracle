#!/usr/bin/env node
import readline from "node:readline";

const ORACLE_MCP_URL = "https://orbitcompute.ai/mcp";

const TOOLS = [
  {
    name: "evaluate_orbital_compute_regime",
    description: "Full physics, 5-year TCO, and credit-underwriting audit for an orbital AI cluster. Use this tool for deep thermodynamic, radiation, Turyshev communication-intensity (bits/J), attrition stress (3.5%/9.0%), $/W payback, and 4-pillar OCEI v2.3 scoring. Do NOT use for fast binary electricity dispatch (use compute_arbitrage_dispatch) or multi-shell percentage routing (use solve_optimal_workload_allocation).",
    inputSchema: {
      type: "object",
      properties: {
        power_mw: { type: "number", minimum: 1, maximum: 100000, default: 100, description: "Target cluster electrical capacity in megawatts (1 to 100,000 MW)." },
        altitude_km: { type: "number", minimum: 300, maximum: 35786, default: 650, description: "Orbital altitude in km (320=VLEO, 650=Dawn-Dusk SSO, 1500=MEO)." },
        beta_deg: { type: "number", minimum: 0, maximum: 90, default: 75, description: "Solar beta angle in degrees (75-90 yields zero eclipse at 650 km)." },
        hw: { type: "string", enum: ["rubin_nvl72", "trillium_tpu_v6e", "blackwell_b200", "terafab_370k"], default: "rubin_nvl72", description: "Orbital AI hardware stack profile." },
        launch_vehicle: { type: "string", enum: ["starship_v3", "starship_v4", "new_glenn_9x4"], default: "starship_v3", description: "Heavy-lift launch vehicle mass and price model." },
        loop_temp_c: { type: "number", minimum: 40, maximum: 120, default: 80, description: "Radiator coolant loop temperature in Celsius (80C optimal for commercial silicon; 95C for Terafab 370K)." },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, default: 115, description: "Custom terrestrial grid tariff in USD/MWh (overrides grid_hub if provided)." },
        grid_hub: { type: "string", enum: ["baseline", "ercot", "pjm", "epex"], default: "baseline", description: "Select live D1 wholesale electricity hub (ercot=Texas, pjm=Virginia, epex=Europe) or canonical $115/MWh baseline." },
        earth_capex_factor: { type: "number", minimum: 0.4, maximum: 1.5, default: 1.0, description: "Terrestrial civil/substation CapEx multiplier (1.0=Tier-IV utility, 0.6=vertically integrated self-build)." },
        annual_attrition_pct: { type: "number", minimum: 0, maximum: 20, default: 0, description: "Annual unrepairable hardware attrition rate in percent (0=raw baseline, 3.5=burn-in screened, 9.0=unscreened stress)." },
        comm_intensity_bits_per_flop: { type: "number", minimum: 1e-11, maximum: 1e-3, default: 1e-8, description: "Workload I/O intensity in bits/FLOP (1e-8=text/reasoning, 2e-6=rich multimodal) for Turyshev Gamma downlink checks." },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live", description: "Space weather telemetry source: live NOAA/GOES streams or deterministic G0/G3/G5 stress profile." }
      }
    }
  },
  {
    name: "compute_arbitrage_dispatch",
    description: "Fast binary go/no-go economic dispatch decision comparing a single terrestrial electricity price or live hub (ERCOT, PJM, EPEX) against the orbital breakeven threshold ($/MWh). Returns exact dispatch_signal (ORBIT_PRIMARY, HYBRID_SPLIT, TERRESTRIAL_PRIMARY), dispatch_directive, breakeven threshold, and $/MTok spread. Use ONLY for binary grid-vs-orbit switching; use solve_optimal_workload_allocation for 3-shell percentage splits.",
    inputSchema: {
      type: "object",
      properties: {
        power_mw: { type: "number", minimum: 1, maximum: 100000, default: 100, description: "Cluster scale in MW used to size launch/bus overhead and breakeven threshold." },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, description: "Explicit local spot electricity price in USD/MWh (supports negative wind/solar spot prices). If omitted, uses grid_hub." },
        grid_hub: { type: "string", enum: ["baseline", "ercot", "pjm", "epex"], default: "ercot", description: "Live wholesale electricity hub to evaluate when grid_price_usd_mwh is omitted." },
        hw: { type: "string", enum: ["rubin_nvl72", "trillium_tpu_v6e", "blackwell_b200", "terafab_370k"], default: "rubin_nvl72", description: "Hardware stack profile determining $/MTok and breakeven $/MWh." },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live", description: "Space-weather mode for pre-emptive storm failover triggers." }
      }
    }
  },
  {
    name: "solve_optimal_workload_allocation",
    description: "Multi-shell percentage constraint solver for cluster schedulers (SkyPilot, Kubernetes, SOOS). Outputs exact percentage splits across 650 km Dawn-Dusk SSO, 320 km self-cleaning VLEO Edge, and Terrestrial Spot Grids based on workload latency SLA, Turyshev downlink intensity (bits/FLOP), space weather, and electricity price. Returns optimal_split_pct and blended $/1M token cost.",
    inputSchema: {
      type: "object",
      properties: {
        workload_type: { type: "string", enum: ["frontier_training", "batch_inference", "realtime_inference"], default: "frontier_training", description: "AI workload class controlling latency sensitivity and batchability." },
        max_latency_ms: { type: "number", minimum: 1, maximum: 10000, default: 45, description: "Maximum acceptable one-way network latency in ms (<=6 ms prioritizes 320 km VLEO)." },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, description: "Spot grid price in USD/MWh; if omitted, uses grid_hub." },
        grid_hub: { type: "string", enum: ["baseline", "ercot", "pjm", "epex"], default: "baseline", description: "Live wholesale electricity hub (ercot, pjm, epex) or $115/MWh baseline." },
        comm_intensity_bits_per_flop: { type: "number", minimum: 1e-11, maximum: 1e-3, default: 1e-8, description: "Turyshev I/O intensity (bits/FLOP); automatically shifts downlink-bound multimodal workloads to Earth." },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live", description: "Space weather regime." }
      }
    }
  },
  {
    name: "get_ocei_history_and_live_grids",
    description: "Retrieves empirical Cloudflare D1 time-series snapshots of OCEI-Spot, true 60-minute settlement TWAP, rolling 30-day covenant availability, and all 3 live wholesale spot electricity hubs (ERCOT Texas, PJM Virginia, EPEX Europe). Use this tool for historical trend comparison, SLA/insurance covenant auditing, or live electricity price lookup.",
    inputSchema: {
      type: "object",
      properties: {
        hours: { type: "number", minimum: 1, maximum: 720, default: 24, description: "Lookback window in hours (1 to 720 hours / 30 days)." },
        limit: { type: "number", minimum: 1, maximum: 200, default: 48, description: "Maximum number of D1 snapshot rows to return." }
      }
    }
  }
];

const rl = readline.createInterface({
  input: process.stdin,
  terminal: false
});

rl.on("line", async (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;
  let req;
  try {
    req = JSON.parse(trimmed);
  } catch (err) {
    process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }) + "\n");
    return;
  }

  if (req.id === undefined || req.id === null) return;

  if (req.method === "initialize") {
    process.stdout.write(JSON.stringify({
      jsonrpc: "2.0",
      id: req.id,
      result: {
        protocolVersion: "2025-03-26",
        capabilities: { tools: {} },
        serverInfo: { name: "mcp-ocei-oracle", version: "2.3.0" }
      }
    }) + "\n");
    return;
  }

  if (req.method === "ping") {
    process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id: req.id, result: {} }) + "\n");
    return;
  }

  if (req.method === "tools/list") {
    process.stdout.write(JSON.stringify({
      jsonrpc: "2.0",
      id: req.id,
      result: { tools: TOOLS }
    }) + "\n");
    return;
  }

  try {
    const res = await fetch(ORACLE_MCP_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(req)
    });
    const data = await res.json();
    process.stdout.write(JSON.stringify(data) + "\n");
  } catch (err) {
    process.stdout.write(JSON.stringify({
      jsonrpc: "2.0",
      id: req.id,
      error: { code: -32603, message: "Upstream OCEI Oracle error: " + err.message }
    }) + "\n");
  }
});
