---
name: BLE Multi-Client Plan
description: Plan for multiple simultaneous iOS device connections (iPad + iPhone) via BLE — DONE, implemented March 2026
type: project
---

# BLE Multi-Client Support — DONE

**Status:** Complete (March 2026)

Implemented per-client targeted BLE notifications so iPad and iPhone can connect simultaneously. Key changes:

- S3: `ble_gatts_notify_custom()` for targeted binary sends, `bleHasClients()` replaces single bool, busy guards for concurrent downloads/uploads, per-client disconnect handling, continue advertising after first connect
- ESP32: reference-counted `statsSubscribeCount` replaces `statsSubscribed` bool
- iOS: defensive guards on BIN_START/BIN_DATA/BIN_END and IMG_ERR to ignore unsolicited frames

See the implementation plan at `.claude/plans/functional-giggling-dahl.md` for full commit-by-commit details.
