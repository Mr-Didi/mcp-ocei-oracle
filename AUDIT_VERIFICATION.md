# Independent Cryptographic & Ledger Audit Verification (`OCEI™ v2.3`)

Any external auditor, credit committee, or autonomous agent can independently verify both live `orbitcompute.ai` oracle responses and the historical SHA-256 hash chain in `ledger/`.

## 1. Verify Live RFC-8785 + ECDSA P-256 (`ES256`) Signature (Browser / Node.js)

```javascript
function canonicalizeRFC8785(obj) {
  if (obj === null || typeof obj !== "object") return JSON.stringify(obj);
  if (Array.isArray(obj)) return "[" + obj.map(canonicalizeRFC8785).join(",") + "]";
  const keys = Object.keys(obj).filter((k) => obj[k] !== undefined).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalizeRFC8785(obj[k])).join(",") + "}";
}

async function auditLiveOracle() {
  const [payload, jwks] = await Promise.all([
    fetch("[https://orbitcompute.ai/v1/index/ocei?format=compact](https://orbitcompute.ai/v1/index/ocei?format=compact)").then((r) => r.json()),
    fetch("[https://orbitcompute.ai/.well-known/jwks.json](https://orbitcompute.ai/.well-known/jwks.json)").then((r) => r.json()),
  ]);
  const att = payload.attestation;
  const unsigned = { ...payload };
  delete unsigned.attestation;

  const bytes = new TextEncoder().encode(canonicalizeRFC8785(unsigned));
  const jwk = jwks.keys.find((k) => k.kid === att.key_id);
  const pubKey = await crypto.subtle.importKey("jwk", jwk, { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);

  const b64 = att.signature.replace(/-/g, "+").replace(/_/g, "/");
  const sig = Uint8Array.from(atob(b64 + "=".repeat((4 - (b64.length % 4)) % 4)), (c) => c.charCodeAt(0));
  const valid = await crypto.subtle.verify({ name: "ECDSA", hash: "SHA-256" }, pubKey, sig, bytes);
  console.log({ valid, key_id: att.key_id, state_hash_sha256: att.state_hash_sha256 });
}
auditLiveOracle();
