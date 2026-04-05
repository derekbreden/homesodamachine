---
name: Stats robustness improvements
description: DONE — 6 stats bugs identified and fixed (subscribe leak, atomic writes, presync edge cases)
type: project
---

# Stats Robustness — DONE

Identified and resolved during robustness review (March 2026).

## Fixes

| # | Issue | Fix | Commit |
|---|-------|-----|--------|
| 1 | Presync double-counting after time sync | Guard `convertPresyncToReal` against repeated execution | 96f4b95 |
| 2 | `statsSubscribed` leaks after BLE disconnect | Two-layer fix: S3 sends `BLE_DISCONNECTED` on disconnect (fast path) + ESP32 CHART_ACK timeout safety net (10s, covers S3 reflash) | 71d3edb |
| 3 | `saveCurrentAccum`/`savePresyncHeader` not atomic | Write-tmp-then-rename pattern | bd0d5d2 |
| 4 | `GET_STATS`/`GET_CHART_DATA` error before time sync | Return zeroed stats instead of error | 44c88b4 |
| 5 | Ring buffer trim has no logging | Added log warning when oldest entries trimmed | f4ecc7b |
| 6 | `convertPresyncToReal` could double-count if re-run | Added guard against repeated execution | 70d0f06 |

## Key design detail (Issue #2)

The subscribe leak fix uses two layers because a single approach can't cover all disconnect scenarios:
- **Layer 1 (fast path):** S3's `onDisconnect` callback sends `BLE_DISCONNECTED` to ESP32, which clears `statsSubscribed`. Covers normal disconnects.
- **Layer 2 (safety net):** ESP32 expects `CHART_ACK` back from S3 for each `CHART_LIVE` sent. If no ack for 10 seconds, auto-unsubscribes. Covers S3 reflash/reboot while ESP32 still has `statsSubscribed = true`.
