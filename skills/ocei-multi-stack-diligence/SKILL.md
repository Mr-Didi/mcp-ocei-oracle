---
name: ocei-multi-stack-diligence
description: Institutional first-principles due diligence, 5-year TCO, $/W payback, hardware attrition stress (3.5%/9.0%), Turyshev Gamma downlink screening, and credit covenant underwriting across divergent orbital compute stacks (StarMind/Rubin, Suncatcher/Trillium, Blackwell, Terafab 370K; Starship V3/V4, New Glenn 9x4).
version: 2.3.0
homepage: https://orbitcompute.ai/dossier
mcp_endpoint: https://orbitcompute.ai/mcp
governance_uri: https://orbitcompute.ai/governance
doi: 10.5281/zenodo.24181722
---

# OCEI™ v2.3 Multi-Stack Engineering & Credit Diligence Skill

Use this skill for CFO capital allocation, infrastructure debt underwriting, parametric space-weather reinsurance modeling, and vendor-neutral architectural benchmarking across orbital AI constellations.

## Primary MCP Tool (`POST https://orbitcompute.ai/mcp`)

- **`evaluate_orbital_compute_regime`** — Executes the full 4-pillar OCEI v2.3 physics and capital model (`AM0 Solar`, `Stefan-Boltzmann T^4 + Earth IR/Albedo`, `25-MW Young-Daly SEU`, `Vacuum OISL + OGS + Turyshev Gamma`) across:
  - **Silicon Stacks (`hw`):** `rubin_nvl72` (250 kW), `trillium_tpu_v6e` (125 kW), `blackwell_b200` (120 kW), `terafab_370k` (250 kW, 95°C knee).
  - **Launch Elasticity (`launch_vehicle`):** `starship_v3` (125t @ $25M), `starship_v4` (200t @ $10M), `new_glenn_9x4` (70t @ $35M).
  - **Skeptic & Credit Stressors:** `earth_capex_factor` (`0.6` vertically integrated self-build vs. `1.0` Tier-IV), `annual_attrition_pct` (`3.5` burn-in screened / `9.0` unscreened stress), `comm_intensity_bits_per_flop` (Turyshev `bit/J` downlink check), and `storm_mode` (`live`, `g0_quiet`, `g3_storm`, `g5_extreme`).

## Key Underwriting Outputs
- `deployed_mass_kg_per_it_kw` (`m_kW`, `15.51 kg/kW` reference) & `mmod_shielded_total_constellation_mass_tons`
- `orbital_5yr_tco_usd_per_watt` (`$33.24/W`) vs. empirical spot revenue payback (`implied_orbital_payback_years`)
- `wacc_adjusted_orbital_lcoc_usd_mtok` (12% orbital WACC vs. 7% terrestrial WACC / `8.26%` IG terrestrial GPU debt reference)
- `covenant_triggers`: binary `storm_interruption_flag`, `rolling_30d_availability_pct`, and `cash_trap_breached` (`<90.0%` floor)
