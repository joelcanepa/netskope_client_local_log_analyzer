# Changes from Stable (v1.9.3 → v1.10.0-beta)

This file tracks all differences between the `beta` branch and the `main` (stable) branch.

---

## New Features

### GTF Check Engine
Integrates a subset of diagnostic checks from Dan Colwell's GTF (Group Troubleshooting Framework) Diagnostic Tool. These run alongside existing ISSUE_PATTERNS and are visually distinguished with a **GTF** badge on each finding card.

**Checks added (17 new, not previously detected):**

| ID | Severity | Category | Description |
|---|---|---|---|
| C-FAILCLOSE | Critical | Tunnel | FailClose flow blocked — connections dropped due to tunnel-down |
| C-TAMPER | Critical | Config | Configuration tampering detected (bypass/exception list modified) |
| C-TEARDOWN | Critical | Tunnel | Gateway-initiated tunnel teardown (threshold: 3+) |
| C-IPC | Critical | Driver | NSCOM2 inter-process communication failure |
| C-BWAN-ENROLL | Critical | SD-WAN | BWAN enrollment / activation DB failure |
| C-BWAN-IFACE | Critical | SD-WAN | BWAN virtual interface (WinTun) creation failed |
| C-BWAN-SSL | Critical | SD-WAN | BWAN DTLS/SSL handshake loop (threshold: 5+) |
| W-DTLS-FALLBACK | Warning | Tunnel | DTLS fell back to TLS — UDP 443 likely blocked |
| W-UPGRADE | Warning | Config | Auto-upgrade failed (signature, installer, or version mismatch) |
| W-PROXYHEALTH | Warning | Tunnel | Proxy health check failed through tunnel |
| C-GSLB-FAIL | Critical | GSLB | GSLB server unreachable — fell back to EDNS/LDNS gateway selection |
| W-GSLB-REEVAL | Warning | GSLB | Frequent GSLB re-evaluations (threshold: 5+, indicates tunnel instability) |
| W-GSLB-SUBOPTIMAL | Warning | GSLB | GSLB PoP stuck — switch thresholds not met repeatedly (threshold: 5+) |
| W-GSLB-CHURN | Warning | GSLB | Excessive GSLB PoP switching (threshold: 3+) |
| W-BWAN-SLEEP | Warning | SD-WAN | BWAN disrupted by device sleep/resume |
| I-RESTARTS | Info | Noise | Client restarted multiple times in log bundle (threshold: 2+) |
| I-POSTURE | Info | Driver | Device posture checks failing |

**Implementation details:**
- GTF checks run via `runGtfChecks()` after `ISSUE_PATTERNS` evaluation in `detectFindings()`
- GTF check patterns are stored in `const GTF_CHECKS` as compact objects
- Pattern parser `_parseGtfRe()` handles single and OR-joined (`/p1/i | /p2/i`) patterns
- Only `simple_count` type checks are executed; `field_match` and `filter_pred` require GTF's event model

### Temporal Flap Detection
New `_detectFlap()` helper performs temporal correlation on log rows — counts connect→disconnect pairs within a sliding time window. Powers two new `matchState` checks:

| ID | Severity | Category | Description |
|---|---|---|---|
| swg-flap | High | Tunnel | SWG tunnel flapping — 3+ cycles in 5-min window |
| npa-flap | Medium | NPA | NPA tunnel flapping — 3+ cycles in 5-min window |

### New Categories
- **SD-WAN** (`sdwan`) — orange `#f0883e` — for BWAN/SD-WAN specific findings
- **GSLB** (`gslb`) — purple `#a371f7` — for GSLB gateway selection findings

---

## Files Changed

| File | Change |
|---|---|
| `index.html` | All above changes — version bumped to `1.10.0-beta` |
| `CHANGES_FROM_STABLE.md` | New file (this document) |

---

## Known Beta Limitations

- GTF `field_match` checks (C-CERT, C-ADMIN, W-TUNNEL-DISC, C-NPA-TUNNEL-SSL, W-NPA-DTLS-ERROR, W-NPA-NETCHANGE-DISCONNECT, W-GSLB-ALLOWLIST) require GTF's structured event model and are **not yet implemented**
- GTF `filter_pred` checks (C-NPA-TRANSPORT-FAIL, I-NPA-GATEWAY-CONNECT, W-GSLB-EGRESS, I-GSLB-V1-FALLBACK, W-GSLB-DTLS-AFTER-SWITCH) require C2 temporal correlation and are **not yet implemented**
- Bypass ratio check (`I-BYPASS-RATIO`) with QUIC exclusion is **not yet implemented**
- Flap detection depends on timestamps being parseable by `new Date()` — rows without timestamps are skipped

---

## Merge Plan (beta → main)

Before merging to `main`:
1. Field-test GTF checks against real log bundles — confirm no false positives
2. Evaluate whether duplicate findings (GTF + our own) are acceptable or need deduplication
3. Implement bypass ratio and any additional high-value `field_match` checks
4. Remove beta label from version, bump to `v1.10.0`
