#!/usr/bin/env node
import readline from "node:readline";

const ORACLE_MCP_URL = "https://orbitcompute.ai/mcp";

const TOOLS = [
  {
    name: "evaluate_orbital_compute_regime",
    description: "Invoke before scheduling batch AI training/inference or evaluating orbital vs. terrestrial compute TCO. Computes OCEI v2.2 Spot/Structural/TWAP scores, L1 shockwave lead time, beta-angle eclipse battery mass, Earth IR/albedo radiator sizing, Silicon Tj throttling, Young-Daly SEU checkpointing, and $/MTok unit economics.",
    inputSchema: {
      type: "object",
      properties: {
        power_mw: { type: "number", minimum: 1, maximum: 100000, default: 100, description: "Target cluster IT power in MW." },
        altitude_km: { type: "number", minimum: 300, maximum: 35786, default: 650, description: "Orbital altitude in km." },
        beta_deg: { type: "number", minimum: 0, maximum: 90, default: 75, description: "Solar beta angle in degrees." },
        hw: { type: "string", enum: ["rubin_nvl72", "trillium_tpu_v6e", "blackwell_b200"], default: "rubin_nvl72" },
        loop_temp_c: { type: "number", minimum: 40, maximum: 120, default: 80, description: "Radiator liquid coolant loop temperature in C." },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, default: 115, description: "Terrestrial electricity price in $/MWh." },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live" }
      }
    }
  },
  {
    name: "compute_arbitrage_dispatch",
    description: "Evaluates real-time spot electricity price ($/MWh) against the orbital breakeven threshold to output a deterministic workload routing directive (ORBIT_PRIMARY, HYBRID_SPLIT, or TERRESTRIAL_PRIMARY).",
    inputSchema: {
      type: "object",
      required: ["grid_price_usd_mwh"],
      properties: {
        power_mw: { type: "number", minimum: 1, maximum: 100000, default: 100 },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, default: 65 },
        hw: { type: "string", enum: ["rubin_nvl72", "trillium_tpu_v6e", "blackwell_b200"], default: "rubin_nvl72" },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live" }
      }
    }
  },
  {
    name: "solve_optimal_workload_allocation",
    description: "Deterministic constraint solver returning the optimal percentage split across 650 km Dawn-Dusk SSO, 320 km VLEO Edge, and Terrestrial Spot Grids based on workload class, max latency tolerance (ms), and electricity spot price.",
    inputSchema: {
      type: "object",
      properties: {
        workload_type: { type: "string", enum: ["frontier_training", "batch_inference", "realtime_inference"], default: "frontier_training" },
        max_latency_ms: { type: "number", minimum: 1, maximum: 10000, default: 45 },
        grid_price_usd_mwh: { type: "number", minimum: -200, maximum: 5000, default: 115 },
        storm_mode: { type: "string", enum: ["live", "g0_quiet", "g3_storm", "g5_extreme"], default: "live" }
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
        serverInfo: { name: "mcp-ocei-oracle", version: "2.2.0" }
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
