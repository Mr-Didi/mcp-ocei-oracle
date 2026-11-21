# OCEI™ v2.3 Benchmark Governance, Neutrality & Fallback Charter

**Administrator:** Spatial Compute Holdings // OrbitCompute Data Consortium  
**Live Charter URI:** `https://orbitcompute.ai/governance`  
**Archival Concept DOI:** `10.5281/zenodo.24181722`

## 1. Conflict-of-Interest & Vendor Neutrality Invariant
OrbitCompute Index Administration operates as a strictly independent open protocol and benchmark publisher. It holds zero proprietary launch vehicles, zero commercial orbital compute clusters, zero sell-side debt underwriting mandates, and accepts zero paid score adjustments from launch, silicon, or hyperscale vendors. All hardware and launch profiles (`rubin_nvl72`, `trillium_tpu_v6e`, `blackwell_b200`, `terafab_370k`, `starship_v3`, `starship_v4`, `new_glenn_9x4`) are evaluated under identical closed-form equations.

## 2. Version Immutability & Methodology Change Notice
Published scoring equations for any major or minor schema (`v2.2.0`, `v2.3.0`) are frozen against silent modification. Material formula changes require:
1. A formal semantic version increment (`v2.x.0`).
2. Advance notice (`30–90 days`) for institutional licensees with Golden-Master backtest deltas.
3. Archival deposit as a new version under Concept DOI `10.5281/zenodo.24181722`.

## 3. Deterministic Telemetry Fallback Cascade (ISDA-Style)
- **Tier 1 (Nominal):** 6 live NOAA/GOES streams + Cloudflare D1 15-minute empirical `OCEI-TWAP-60m` (`D1_EMPIRICAL_60M`) + 3 live wholesale electricity hubs (`ERCOT Texas`, `PJM Virginia`, `EPEX DE-LU`).
- **Tier 2 (Upstream Outage <60 min):** Last verified D1 snapshot carried forward with decaying `confidence_score`.
- **Tier 3 (Extended Outage >60 min):** Deterministic fallback to weather-invariant `OCEI-Structural` (5-year baseline) and canonical `$115/MWh` Tier-IV tariff, explicitly flagged in `telemetry_status` and `twap_60m_source`.

## 4. Cryptographic Key Retention & Dual-Anchor Audit Trail
- Active responses are canonicalized per **IETF RFC 8785 (JCS)** and signed via **ECDSA P-256 (`ES256`)** using hardware-isolated Cloudflare Secrets (`kid: ocei-es256-global-v2.3`).
- Retired public keys (including `ocei-es256-global-v2.2`) are permanently retained in `https://orbitcompute.ai/.well-known/jwks.json` to ensure 5-to-12-year debt and parametric insurance verifiability.
- Empirical state history is dual-anchored in **Cloudflare D1** (15-minute cadence) and this public **SHA-256 hash-chained GitHub ledger** (`ledger/YYYY-MM.jsonl`).
